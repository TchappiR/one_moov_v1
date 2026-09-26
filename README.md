# One Moov — version finalisée (v1 web)

Application d'aide à la mobilité étudiante (Afrique francophone → France), à partir
de la base de Dorcas, finalisée selon les 6 instructions.

**Principe de fiabilité :** les faits (formations, RNCP, montants, étapes) viennent de
la **base**, jamais du LLM. Le modèle ne fait que dialoguer et mettre en forme.

## Ce qui est implémenté (mappé aux instructions)

| # | Instruction | Où |
|---|---|---|
| 1 | Conseiller d'orientation (projet pro + académique) → **10 formations** gratuites | `routers/orientation.py`, `services/orientation_engine.py` (scoring déterministe) |
| 2 | Parcours **public / privé** ; en privé, **vérif RNCP** et déconseil si absent | `routers/roadmap.py`, `routers/rncp.py`, `services/rncp_client.py` (France Compétences en direct) |
| 3 | Roadmap **admission → voyage** en arbre | `data/procedures/france.py`, `services/roadmap_engine.py` |
| 4 | Partie 2 **payante** via agrégateur africain (**CinetPay**, mobile money) | `routers/paiement.py`, `services/cinetpay.py` |
| 5 | **Chatbot popup** de procédure (partie payante) | `routers/chatbot.py`, front `ChatbotPopup` |
| 6 | **Pilotage des tokens** : coût global + par utilisateur, rentabilité < 100 € | `services/token_meter.py`, `routers/metrics.py` |

Autres : comptes e-mail + mot de passe (JWT), LLM **Groq uniquement** (cascade de modèles
+ mode guidé sans IA), PostgreSQL (SQLite en repli pour démarrer), frontend **React/Vite**
responsive (mobile plus tard).

## Fonctionnalités avancées (réintégrées de la v1)

Ces éléments enrichissent l'expérience sans jamais trahir le principe de fiabilité
(faits en base, IA seulement pour dialoguer/mettre en forme) :

| # | Fonctionnalité | Où |
|---|---|---|
| 1 | **Rapport d'orientation structuré** (synthèse, atouts, points d'attention) | `routers/orientation.py` (`/rapport`), `prompts.py` (`SYSTEM_RAPPORT`), front `Rapport` |
| 2 | **Transparence** « comment ces pistes sont trouvées » (méthode déterministe explicitée) | `routers/orientation.py` (`TRANSPARENCE`), front `Rapport` |
| 3 | **Moteur d'échéances** : date cible par étape, décompte, urgence, prochaine action enrichie | `services/roadmap_engine.py`, `data/procedures/france.py` (`avant_rentree_jours`) |
| 5 | **Deux vues** de la feuille de route : **Arbre** (par phase) et **Liste** (chronologique) | front `Roadmap` (bascule `Arbre/Liste`) |
| 6 | **Modale d'étape** + **confirmation des étapes critiques** | front `StepModal` ; `critique` dans `data/procedures/france.py` |
| 7 | **Entonnoir par niveau** (L1/DAP, L2-L3, Master, BTS) — la procédure s'adapte | `data/procedures/france.py` (`NIVEAUX`, `ADAPTATIONS`), `routers/roadmap.py` (`/niveaux`) |
| 10 | **Simulation d'entretien Campus France** (entretien blanc + bilan) | `routers/aides.py` (`/entretien`), `prompts.py` (`SYSTEM_ENTRETIEN`), front `EntretienModal` |
| 11 | **Aide à la contestation d'un refus** (voies, conseils, brouillon de courrier) | `routers/aides.py` (`/contestation`), front `ContestationModal` |
| 14 | **Tableau de bord des pistes** (tous les projets, avancement, prochaine échéance) | `routers/pistes.py` (`GET /pistes`), front `Dashboard` |
| 15 | **Finitions design** (barres de progression, badges, urgences colorées, modales) | `styles.js`, `App.jsx` |

> Non retenus pour cette version : rappels WhatsApp, coach CV, lettre de motivation, module bourse.

## Démarrer

### 1. Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # optionnel
pip install -r requirements.txt
cp .env.example .env               # renseigner les clés (voir ci-dessous)
python -m app.scripts.sync_rncp    # synchronise le référentiel RNCP (une fois — télécharge l'export officiel)
uvicorn app.main:app --reload      # http://localhost:8000  · doc : /docs
```
Sans `DATABASE_URL`, l'app démarre sur **SQLite** (`onemoov.db`). Sans `GROQ_API_KEY`,
elle tourne en **mode guidé** (questionnaire fixe) — parfait pour une démo.

### 2. Frontend
```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173 (proxy /api -> 8000)
# ou build de prod : npm run build  (servi automatiquement par le backend)
```

## Clés à fournir (.env) pour l'usage réel

- `GROQ_API_KEY` — moteur LLM (console.groq.com).
- `DATABASE_URL` — PostgreSQL (ex. Supabase / Neon / Render).
- `CINETPAY_API_KEY`, `CINETPAY_SITE_ID`, `CINETPAY_MODE=PRODUCTION` — paiement réel
  (sinon **SANDBOX** : page de paiement simulée pour tester le parcours).
- `OPEN_DATA_FORMATIONS_URL` — dataset ONISEP/Mon Master/Parcoursup (sinon instantané
  de repli `data/seed/formations_fallback.json`).
- **RNCP** — pas de clé : `python -m app.scripts.sync_rncp` télécharge l'export officiel
  France Compétences (data.gouv.fr) dans la base, puis la vérification est un lookup local.

## Reste à faire avant la production (assumé)

- Lancer `python -m app.scripts.sync_rncp` (télécharge l'export RNCP officiel) ; adapter
  le mapping des colonnes CSV dans `data/ingestion/rncp.py` si le format évolue. À reprogrammer périodiquement (export quotidien).
- Brancher le dataset open data réel des formations (mapping dans `data/ingestion/onisep.py`).
- Compte marchand CinetPay + test du webhook signé.
- Restreindre `/api/admin/costs` aux comptes admin ; restreindre CORS en prod.
- Vérifier une à une les valeurs du pack procédure (`data/procedures/france.py`).

## Pilotage des tokens (instruction 6)

Chaque appel LLM enregistre tokens + coût (`token_meter`). Tableau de bord :
`GET /api/admin/costs` → coût global, coût **moyen par utilisateur**, budget mensuel,
et **rentabilité** (marge vs prix de vente). La grille de prix Groq se règle dans
`services/token_meter.py`. Frugalité : petit modèle Groq pour les tâches simples,
scoring **déterministe** au lieu du LLM pour le matching, historique tronqué, mode guidé.
