"""Central config — reads .env, fails clearly if required keys missing."""
from __future__ import annotations
import os
from dotenv import load_dotenv

# override=False so explicitly-set env vars (shell, test harness, Railway)
# win over values in .env on disk.
load_dotenv(override=False)


def _get(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


# Server
HOST = _get("HOST", "0.0.0.0")
PORT = int(_get("PORT", "8000"))
VAPI_SECRET = _get("VAPI_SECRET")
PUBLIC_BASE_URL = _get("PUBLIC_BASE_URL", "").rstrip("/")

# Stripe
STRIPE_SECRET_KEY = _get("STRIPE_SECRET_KEY")
STRIPE_SUCCESS_URL = _get("STRIPE_SUCCESS_URL", "https://example.com/success")
STRIPE_CANCEL_URL = _get("STRIPE_CANCEL_URL", "https://example.com/cancel")
STRIPE_WEBHOOK_SECRET = _get("STRIPE_WEBHOOK_SECRET")   # from Stripe webhook config

# Twilio (SMS)
TWILIO_ACCOUNT_SID = _get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = _get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = _get("TWILIO_FROM_NUMBER")

# Supabase (optional — when both set, store switches from memory to Supabase)
SUPABASE_URL = _get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = _get("SUPABASE_SERVICE_KEY")   # server-only (service_role)

# Admin page (Basic auth)
ADMIN_USER = _get("ADMIN_USER", "admin")
ADMIN_PASS = _get("ADMIN_PASS", "admin")


def is_configured() -> bool:
    """True when the real (non-placeholder) credentials are present."""
    return bool(STRIPE_SECRET_KEY) and STRIPE_SECRET_KEY != "sk_test_xxx" \
        and bool(TWILIO_ACCOUNT_SID) and bool(TWILIO_AUTH_TOKEN) and bool(TWILIO_FROM_NUMBER)


def using_supabase() -> bool:
    """True when Supabase is wired up — store auto-switches to it."""
    return bool(SUPABASE_URL) and bool(SUPABASE_SERVICE_KEY)
