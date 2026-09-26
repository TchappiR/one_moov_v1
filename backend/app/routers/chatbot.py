"""
routers/chatbot.py — Chatbot popup de la partie payante (instruction 5).

Répond aux questions de procédure de l'étudiant, ANCRÉ sur le contenu vérifié de
l'étape en cours (il ne réinvente pas la procédure). Réservé aux pistes payées.
Mode guidé (sans IA) : renvoie le conseil et les documents officiels de l'étape.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.deps import get_current_user
from app.models import User, Piste
from app.schemas import ChatbotIn
from app.services.llm import get_llm, Meter, LLMUnavailable
from app.services.roadmap_engine import etape_par_id

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

SYSTEME = ("Tu es l'assistant procédure de One Moov, pour un étudiant qui prépare sa "
           "mobilité vers la France. Réponds en français, de façon concrète et rassurante, "
           "en t'appuyant UNIQUEMENT sur le contexte d'étape fourni. Si l'info n'y est pas, "
           "dis-le et renvoie vers la source officielle. N'invente jamais un montant, une "
           "date ou une règle.")


@router.post("")
def chatbot(body: ChatbotIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = db.get(Piste, body.piste_id)
    if not p or p.user_id != user.id:
        raise HTTPException(404, "Piste introuvable")
    if not p.paid:
        raise HTTPException(402, "Le chatbot fait partie de la formule payante.")

    niveau = (p.roadmap or {}).get("niveau") or ""
    etape = etape_par_id(body.etape, niveau) if body.etape else None
    contexte = ""
    if etape:
        echeance = ""
        for e in _etapes_roadmap(p):
            if e.get("id") == body.etape and e.get("echeance_str"):
                echeance = f"\nÉchéance conseillée : {e['echeance_str']} ({e.get('jours_restants')} j)"
                break
        contexte = (f"Étape : {etape['label']}\nConseil vérifié : {etape['conseil']}\n"
                    f"Documents : {', '.join(etape['docs']) or 'aucun'}{echeance}")

    llm = get_llm()
    msgs = [{"role": m.role, "content": m.content} for m in body.messages]

    if not llm.available:
        return {"content": _guide(etape), "mode": "guidé"}
    try:
        system = SYSTEME + (f"\n\nContexte de l'étape :\n{contexte}" if contexte else "")
        meter = Meter(db=db, endpoint="chatbot", user_id=user.id, piste_id=p.id)
        # frugalité : petit modèle Groq pour ces réponses courtes
        text = llm.chat(msgs, system=system, max_tokens=400, temperature=0.5,
                        leger=True, meter=meter)
        return {"content": text, "mode": "IA"}
    except LLMUnavailable:
        return {"content": _guide(etape), "mode": "guidé"}


def _etapes_roadmap(p: Piste) -> list[dict]:
    out = []
    for ph in (p.roadmap or {}).get("phases", []):
        out.extend(ph.get("etapes", []))
    return out


def _guide(etape) -> str:
    if not etape:
        return "Sélectionne une étape et je te donne les documents et le conseil officiel."
    return (f"{etape['conseil']}\n\nDocuments nécessaires : "
            f"{', '.join(etape['docs']) or 'aucun'}.\nEn cas de doute, réfère-toi à la source officielle.")
