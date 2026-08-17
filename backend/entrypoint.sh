#!/bin/sh
set -e

echo "Esperando a que la base de datos este lista..."
python -c "
import time, sys
from sqlalchemy import create_engine, text
from app.core.config import settings
for i in range(30):
    try:
        create_engine(settings.DATABASE_URL).connect().close()
        sys.exit(0)
    except Exception:
        time.sleep(2)
sys.exit(1)
"

echo "Aplicando migraciones..."
alembic upgrade head

echo "Sembrando roles y usuario administrador base..."
python seed_roles.py

echo "Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
