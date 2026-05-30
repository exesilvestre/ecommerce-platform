# Seed

Demo data: 1 customer, 4 Apple products, 4 US warehouses with intentional inventory gaps.

See **[../ASSESSMENT.md](../ASSESSMENT.md)** for product/warehouse IDs and test scenarios.

Reads configuration from **`../.env`** (the backend `.env`).

```bash
cd backend
source .venv/bin/activate
python seed/load_seed.py
```

Optional: `python seed/load_seed.py --file seed/data/seed.json`
