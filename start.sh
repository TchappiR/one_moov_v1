#!/usr/bin/env bash
# Démarre le backend One Moov (sert aussi le frontend buildé s'il existe).
set -e
cd "$(dirname "$0")/backend"
[ -f .env ] || cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
