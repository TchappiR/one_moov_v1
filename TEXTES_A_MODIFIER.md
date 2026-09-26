# Où modifier les textes vus par l'utilisateur

Petit guide pour retrouver **chaque texte affiché à l'écran** et le modifier.

> ⚙️ Après modification :
> - **texte du frontend** (fichiers `frontend/src/…`) → relancez `npm run build` (ou l'app Docker), puis rafraîchissez (Ctrl+Shift+R) ;
> - **texte du backend** (fichiers `backend/app/…`) → il suffit de **redémarrer** le serveur (`uvicorn …`).

---

## 1. Interface : boutons, titres, libellés, écrans

📄 `frontend/src/App.jsx` — tout ce qui est affiché dans l'app est dans des composants nommés :

| Ce que vous voyez | Composant à éditer |
|---|---|
| Écrans de connexion / inscription / vérification e-mail / mot de passe oublié | `Auth` |
| Accueil + liste des projets (tableau de bord) | `Dashboard` |
| Bulles d'accueil du conseiller (1ers messages du chat) | `Orientation` → constante `GREET` |
| Rapport d'orientation (titres « Vos atouts », « À travailler »…) | `Rapport` |
| « Comment ces pistes sont trouvées » (à la reprise) | `App.jsx` → constante `TRANSPARENCE` (voir aussi §5) |
| Choix voie / niveau / vérif RNCP / bouton de paiement | `Parcours` |
| Feuille de route (en-tête, stats, vues Arbre/Liste) | `Roadmap` / `TreeView` / `StepRow` |
| Fenêtre de détail d'une étape | `StepModal` |
| Entretien Campus France (fenêtre) | `EntretienModal` |
| Contester un refus (formulaire + résultat) | `ContestationModal` |

🎨 Couleurs, polices, styles → `frontend/src/styles.js` (objet `C` + `GLOBAL_CSS`).

---

## 2. Ce que « dit » l'IA (conversations et textes générés)

📄 `backend/app/prompts.py` — les consignes données aux modèles :

| Texte | Variable |
|---|---|
| Personnalité et questions du **conseiller d'orientation** | `SYSTEM_ORIENTATION` |
| Rédaction de la **synthèse** du rapport | `SYSTEM_RAPPORT` / `RAPPORT_TEMPLATE` |
| **Entretien** Campus France (rôle, déroulé) + phrase d'ouverture | `SYSTEM_ENTRETIEN` / `ENTRETIEN_OUVERTURE` |
| **Contestation** d'un refus | `SYSTEM_CONTESTATION` / `CONTESTATION_TEMPLATE` |
| **Mode guidé** (sans clé IA) : questions d'orientation | `GUIDE_ETAPES` |
| **Mode guidé** : questions d'entretien | `ENTRETIEN_QUESTIONS_GUIDE` |

📄 `backend/app/routers/chatbot.py` → `SYSTEME` : l'assistant de procédure (Q&R).

---

## 3. Contenu de la feuille de route (étapes, conseils, échéances, niveaux)

📄 `backend/app/data/procedures/france.py` :
- `ETAPES_FRANCE` : chaque étape (titre `label`, `conseil`, `docs`, échéance `avant_rentree_jours`, `critique`) ;
- `NIVEAUX` : les 4 niveaux de l'entonnoir (L1/DAP, L2-L3, Master, BTS/BUT) ;
- `ADAPTATIONS` : les textes qui changent selon le niveau (ex. procédure DAP en L1).

---

## 4. Les formations proposées (le catalogue)

📄 `backend/app/data/seed/formations_fallback.json` — ajoutez / modifiez les fiches
(intitulé, établissement, ville, domaine, niveau, voie, coût). C'est ce catalogue qui
alimente les 10 pistes. Après édition, relancez l'ingestion (elle recharge au démarrage
si la table est vide, ou forcez via `charger_formations(db, force=True)`).

Le **classement** (poids domaine/niveau/budget/ville) se règle dans
`backend/app/services/orientation_engine.py`.

---

## 5. Textes « fiabilité » / transparence

- Explication « comment ces pistes sont trouvées » : `backend/app/routers/orientation.py` → `TRANSPARENCE`
  (et la copie d'affichage à la reprise dans `frontend/src/App.jsx` → `TRANSPARENCE`).
- Messages de **vérification RNCP** :
  - via LLM web → `backend/app/services/rncp_web.py` (fonction `_map`) ;
  - repli export officiel → `backend/app/services/rncp_client.py` (fonction `_verdict` / `_res`).
- Aide à la **contestation** en mode guidé (voies, conseils, lettre type) :
  `backend/app/routers/aides.py` → `_contestation_guide`.

---

## 6. E-mails, pages système, paiement, prix

- E-mails de vérification / réinitialisation + pages HTML de confirmation :
  `backend/app/routers/auth.py` (`_mail_html`, `_page`, `reset_page`).
- Page de paiement (sandbox) : `backend/app/routers/paiement.py` (fonction `sandbox`).
- **Prix** : `backend/app/config.py` → `PRIX_PARCOURS_EUR` et `TAUX_EUR_FCFA`
  (l'affichage en FCFA côté écran est dans `frontend/src/App.jsx` : `PRIX_FCFA` / fonction `fcfa`).
