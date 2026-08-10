# HANDOFF — evening setup (Vapi + Supabase)

Everything is coded and committed. When you have your **Vapi** and **Supabase**
accounts, do these steps. No code changes needed.

## 1. Supabase (data persistence)
1. supabase.com → New project (free). Wait for it to provision.
2. Project → SQL Editor → **open `supabase_schema.sql` (in this repo)** → Run.
   This creates `menu`, `orders`, `reservations` tables.
3. Settings → API → copy **Project URL** and **service_role key** (secret — server only).
4. Add to `.env` (or Railway Variables):
   ```
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_SERVICE_KEY=eyJ...service_role...
   ```
   The app auto-switches from in-memory to Supabase the moment both are set.
5. (Optional) Seed the Hakka Legend menu into Supabase by running the app once
   locally with `python scripts/seed_supabase.py` (reads `app/seed.py`). Or just
   use the admin page after deploy — the menu is already loaded in-memory and the
   admin "add" works against Supabase too.

## 2. Stripe (pay-by-link)
1. stripe.com → get **secret key** (use test mode first: `sk_test_...`).
2. Add to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_SUCCESS_URL=https://your-domain/order-success
   STRIPE_CANCEL_URL=https://your-domain/order-cancel
   ```
3. Dashboard → Webhooks → **Add endpoint** →
   URL: `<PUBLIC_BASE_URL>/stripe/webhook`, events: `checkout.session.completed`.
   Copy the **signing secret** → `STRIPE_WEBHOOK_SECRET`.

## 3. Twilio (SMS)
1. twilio.com → get Account SID, Auth Token, a Twilio number.
2. Add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_FROM_NUMBER=+1...
   ```

## 4. Vapi (voice)
1. vapi.ai → create an assistant from `vapi_assistant.json`:
   - replace `{{PUBLIC_BASE_URL}}` with your deploy URL.
   - keep the system prompt (already set to Hakka Legend, Markham).
2. Buy a phone number in Vapi, attach the assistant.
3. (Optional) set a secret in Vapi and `VAPI_SECRET` in `.env` to verify calls.

## 5. Deploy (Railway)
1. Push this repo to GitHub (already committed locally).
2. Railway → New Project → Deploy from GitHub.
3. Add all env vars above (see `RAILWAY_ENV.md`).
4. Deploy → copy the `*.up.railway.app` URL → set `PUBLIC_BASE_URL` → redeploy.
5. Done. Call the Vapi number and test.

## Test locally first (no accounts needed)
```bash
source venv/bin/activate
uvicorn app.main:app --reload
# admin page: http://localhost:8000/admin  (admin / change_me — change in .env)
pytest -q   # 9 smoke tests
```

## What's verified
- 138-item Hakka Legend (Markham) menu, 10 categories.
- Protein options + soup size pricing (e.g. seafood noodle $16, soup medium $9.99).
- Order + reservation creation, admin auth + CRUD, Stripe webhook flips order to PAID.
- All of the above pass the pytest suite (in-memory mode).
