# Seed

One-off demo data load (customer, products, warehouses, inventory).

Reads configuration from **`../.env`** (the backend `.env`).

```bash
cd backend
source .venv/bin/activate
python seed/load_seed.py
```

Optional: `python seed/load_seed.py --file seed/data/seed.json`
