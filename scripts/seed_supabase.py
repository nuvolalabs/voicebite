"""Seed the Hakka Legend menu into Supabase. Run once after creating the project:
    source venv/bin/activate
    python scripts/seed_supabase.py
Requires SUPABASE_URL + SUPABASE_SERVICE_KEY in .env.
"""
from __future__ import annotations
import os
import sys

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not (SUPABASE_URL and SUPABASE_SERVICE_KEY):
    print("ERROR: set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env first.")
    sys.exit(1)

from supabase import create_client
from app.seed import MENU

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Upsert all menu items (id is primary key, so re-running is safe).
rows = [
    {
        "id": m["id"],
        "name": m["name"],
        "category": m["category"],
        "price": float(m["price"]),
        "options": m.get("options", []),
        "option_prices": m.get("option_prices", {}),
    }
    for m in MENU.values()
]

# Insert in chunks to be safe with payload size.
CHUNK = 50
for i in range(0, len(rows), CHUNK):
    sb.table("menu").upsert(rows[i : i + CHUNK]).execute()

print(f"Seeded {len(rows)} menu items into Supabase.")
