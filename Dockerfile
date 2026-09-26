# One Moov — image unique (frontend buildé + backend FastAPI qui le sert)
# Build : docker build -t one-moov .
# Run   : docker run -p 8000:8000 --env-file backend/.env one-moov

# --- Étape 1 : build du frontend React ---
FROM node:20-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Étape 2 : backend FastAPI + frontend servi ---
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install -r backend/requirements.txt
COPY backend/ backend/
COPY --from=frontend /app/frontend/dist frontend/dist
WORKDIR /app/backend
EXPOSE 8000
# $PORT est fourni par l'hébergeur (Render) ; 8000 en local.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
