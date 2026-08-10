# voip-restaurant

Lean voice-agent backend for restaurants: answers calls via **Vapi**, takes
**takeout orders** and **table reservations**, and sends a **Stripe payment link
by SMS** (Twilio). FastAPI tool-server + admin page, deployable to Railway.

## Deploy (Railway — one click)
1. Push this repo to GitHub.
2. In Railway: *New Project → Deploy from GitHub* → select this repo.
3. Add the env vars listed in `RAILWAY_ENV.md` (Stripe, Twilio, admin password).
4. Deploy. Copy the generated `https://*.up.railway.app` URL.
5. Set `PUBLIC_BASE_URL` to that URL, redeploy.
6. In `vapi_assistant.json`, replace `{{PUBLIC_BASE_URL}}` with the URL, create
   the assistant in Vapi, buy a phone number, attach it.

## Local dev
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness |
| GET | `/restaurant` | restaurant profile |
| POST | `/tools/get_menu` | menu (optional category) |
| POST | `/tools/create_order` | takeout order → total |
| POST | `/tools/create_reservation` | table booking |
| POST | `/tools/send_payment_link` | Stripe link + SMS |
| GET | `/admin` | admin page (Basic auth) |

See `README.md` for full details.
