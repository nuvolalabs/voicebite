"""Test isolation: force the in-memory backend regardless of a real .env.

app.config calls load_dotenv() at import time, which re-reads .env from disk.
When a real .env sets SUPABASE_URL/SUPABASE_SERVICE_KEY (the normal production
case), that import would flip the store to Supabase and break these in-memory
smoke tests. We pop the vars and stub load_dotenv before any app import so the
fixture's in-memory intent always wins.
"""
import os

os.environ.pop("SUPABASE_URL", None)
os.environ.pop("SUPABASE_SERVICE_KEY", None)

import dotenv

dotenv.load_dotenv = lambda *a, **k: False  # no-op during tests
