# One Moov — Guide de lancement & de test

Ce guide couvre trois choses :

- **A. Lancer l'app en local** (sur ton PC).
- **B. La faire tester tout de suite** par d'autres (tunnel, lien temporaire).
- **C. La déployer en ligne** (lien public permanent, hébergé).

Le frontend est **déjà compilé** dans `frontend/dist` : pour un simple lancement,
tu n'as pas besoin de Node — le backend sert l'app tout seul.

---

## Pré-requis

- **Python 3.11+** (`python --version`)
- **Node 18+** *(seulement si tu modifies le frontend)*
- **Une clé Groq** (facultatif) sur https://console.groq.com → active le **mode IA**.
  Sans clé, l'app tourne en **mode guidé** (questionnaire fixe) : parfait pour une démo.

---

## A. Lancer en local (Windows / PowerShell)

```powershell
cd one-moov-finalise\backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1        # (ou .\.venv\Scripts\activate.bat en CMD)

pip install -r requirements.txt
copy .env.example .env               # puis ouvre .env et renseigne tes clés (voir plus bas)

python -m app.scripts.sync_rncp      # facultatif : télécharge le référentiel RNCP officiel
uvicorn app.main:app --reload
```

Ouvre ensuite **http://localhost:8000** — l'app complète est là (doc API sur `/docs`).

> Sans `DATABASE_URL`, l'app démarre sur **SQLite** (fichier `onemoov.db`), rien à installer.

*Pour modifier le frontend :* `cd frontend` → `npm install` → `npm run dev` (port 5173, dev)
ou `npm run build` (recompile ce que sert le backend).

---

## B. Faire tester tout de suite (tunnel Cloudflare — gratuit, sans compte)

Idéal pour montrer l'app à quelques proches **maintenant**. Ton PC doit rester
allumé et le serveur lancé pendant les tests.

1. Lance le backend en local (**étape A**) — il écoute sur le port **8000**.
2. Installe `cloudflared` (dans une **autre** fenêtre PowerShell) :

   ```powershell
   winget install --id Cloudflare.cloudflared
   ```
   *(ou télécharge `cloudflared-windows-amd64.exe` depuis le site de Cloudflare)*

3. Ouvre le tunnel :

   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```

4. Cloudflare affiche une URL du type **`https://xxxx-xxxx.trycloudflare.com`**.
   Partage-la : tes testeurs y accèdent depuis n'importe où.

**Bon à savoir**
- L'URL **change** à chaque redémarrage du tunnel (c'est un lien jetable).
- Le paiement **sandbox** fonctionne à travers le tunnel (lien relatif).
- Pour que les testeurs voient l'**IA**, mets ta `GROQ_API_KEY` dans `backend/.env`.

---

## C. Déployer en ligne (Render — lien permanent)

Un vrai lien public, l'app tourne **24/7** sans ton PC. Gratuit. Le projet contient
déjà tout le nécessaire : `Dockerfile` + `render.yaml`.

**Pré-requis :** un compte **GitHub** et un compte **Render** (render.com), tous deux gratuits.

### 1) Mettre le code sur GitHub

```powershell
cd one-moov-finalise
git init
git add .
git commit -m "One Moov finalisé"
git branch -M main
git remote add origin https://github.com/TON-COMPTE/one-moov.git
git push -u origin main
```

### 2) Déployer sur Render

1. Sur **render.com** → **New +** → **Blueprint**.
2. Connecte ton dépôt GitHub → Render lit `render.yaml` et propose **un service web
   (Docker) + une base PostgreSQL** gratuite. Clique **Apply**.
3. Dans le service créé → onglet **Environment** → renseigne **`GROQ_API_KEY`**
   (ta clé Groq). `JWT_SECRET` et `DATABASE_URL` sont déjà remplis automatiquement,
   `CINETPAY_MODE` reste `SANDBOX`.
4. Attends le 1er déploiement (~5-10 min). Render te donne une URL type
   **`https://one-moov.onrender.com`** → c'est le lien à partager.
5. *(Optionnel)* remets cette URL dans la variable **`PUBLIC_BASE_URL`** (utile seulement
   pour un vrai paiement CinetPay, pas pour le sandbox).
6. *(Optionnel)* pour la vérification RNCP fiable : onglet **Shell** du service →
   `cd /app/backend && python -m app.scripts.sync_rncp`.

**Bon à savoir (offre gratuite)**
- Le service **s'endort** après ~15 min sans visite et se **réveille en ~30 s** au 1er accès.
- La base PostgreSQL gratuite **expire après ~90 jours** (à recréer ensuite).
- À chaque `git push`, Render **redéploie** automatiquement.

---

## D. Ce que font tes testeurs

1. Ils ouvrent le lien (tunnel ou Render).
2. Ils **créent leur propre compte** (e-mail + mot de passe — pas de vérification e-mail).
3. Orientation gratuite → **rapport** (10 pistes) → **parcours** (public/privé, niveau)
   → **paiement** : en sandbox, bouton « **Payer (simuler un succès)** » → **feuille de
   route** avec échéances, entretien blanc Campus France et aide à la contestation.

Avec `GROQ_API_KEY` → expérience **IA** ; sans clé → **mode guidé**. L'app marche dans les deux cas.
Ce sont des comptes de **test** : n'y mets pas de vraies données personnelles.

---

## E. Variables d'environnement (`backend/.env`)

| Variable | Rôle | Défaut |
|---|---|---|
| `GROQ_API_KEY` | Active le mode IA (console.groq.com) | vide → mode guidé |
| `DATABASE_URL` | PostgreSQL en prod (`postgres://…` accepté, converti tout seul) | vide → SQLite local |
| `JWT_SECRET` | Signature des jetons de connexion | `change-me-in-production` |
| `CINETPAY_MODE` | `SANDBOX` (paiement simulé) ou `PRODUCTION` | `SANDBOX` |
| `CINETPAY_API_KEY` / `CINETPAY_SITE_ID` | Compte marchand pour le vrai paiement | vide |
| `PUBLIC_BASE_URL` | URL publique (pour CinetPay production) | `http://localhost:8000` |

RNCP : pas de clé — `python -m app.scripts.sync_rncp` télécharge l'export officiel
France Compétences (à relancer périodiquement).
