#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os
import sys
import time

from sqlalchemy import create_engine, text

url = os.environ["DATABASE_URL_SYNC"]
engine = create_engine(url)

for attempt in range(30):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("PostgreSQL is ready")
        sys.exit(0)
    except Exception as exc:
        print(f"Waiting... ({attempt + 1}/30): {exc}")
        time.sleep(2)

print("PostgreSQL did not become ready in time")
sys.exit(1)
PY

echo "Running migrations..."
alembic upgrade head

echo "Checking if seed is needed..."
python - <<'PY'
import os
import subprocess
import sys

from sqlalchemy import create_engine, text

url = os.environ["DATABASE_URL_SYNC"]
engine = create_engine(url)

with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()

if count == 0:
    print("Empty catalog — loading seed data...")
    subprocess.check_call([sys.executable, "seed/load_seed.py"])
else:
    print(f"Catalog has {count} products — skipping seed")
PY

exec uvicorn main:app --host 0.0.0.0 --port 8000
