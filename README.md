# Restaurant Voice Agent (MVP)

A lean voice-agent backend for restaurants: answers calls, takes **takeout orders**
and **table reservations**, and sends a **Stripe payment link by SMS**. Powered by
**Vapi** for the voice/telephony and **FastAPI** for the tool server.

## Architecture
```
Caller -> Vapi (STT + LLM + TTS, telephony)
                 |
                 |  tool calls (HTTP POST)
                 v
        FastAPI tool server  <-->  in-memory store (Supabase-ready)
                 |
                 |  create payment link + SMS
                 v
              Stripe  +  Twilio
```

## Quickstart
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in real keys (works in demo mode without them)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

In demo mode (no keys) the server still runs and prints SMS/payment links to the
terminal instead of sending them — handy for end-to-end testing without accounts.

## Expose to Vapi
Vapi must reach these endpoints over the public internet. Deploy to Railway/Render,
or tunnel locally:
```bash
ngrok http 8000    # then set PUBLIC_BASE_URL in .env to the https URL
```
In `vapi_assistant.json`, replace `{{PUBLIC_BASE_URL}}` with that URL and create the
assistant in the Vapi dashboard (or via the Vapi API).

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET  | `/health` | liveness + config check |
| POST | `/tools/get_menu` | menu (optional category) |
| POST | `/tools/create_order` | create takeout order -> returns total |
| POST | `/tools/create_reservation` | book a table |
| POST | `/tools/send_payment_link` | Stripe link + SMS to phone |

## Seed menu (Hakka Legend — Markham)
The store ships seeded with the **Hakka Legend** takeout menu (138 items, 10
categories: appetizers, soups, noodles, rice, chef, chicken, seafood, vegetarian,
thai, lunch). The assistant is configured for the **Markham** location
(phone 905.294.5777, Mon-Thu 11-10 / Fri-Sat 11-11 / Sun 12-10). Profile lives in
`app/restaurant.py` — edit there to switch locations or go multi-tenant.
Dishes with protein/style choices expose an `options` list so the voice agent can
offer "chicken, beef, shrimp, or veg?"; soups expose size-based `option_prices`
(small/medium/large). Edit the menu live from the admin page.
A single-page admin (served by the same FastAPI app, no separate build) for editing the
menu and watching live orders/reservations. Protected by HTTP Basic auth.

```
GET  /admin            -> the page (login: ADMIN_USER / ADMIN_PASS)
GET  /admin/api/menu   -> list menu
POST /admin/api/menu   -> add item  {name, category, price}
PUT  /admin/api/menu   -> update item {id, name, category, price}
DEL  /admin/api/menu   -> delete item {id}
GET  /admin/api/orders -> live orders (auto-refreshes every 8s)
GET  /admin/api/reservations -> live reservations
```

Set `ADMIN_USER` / `ADMIN_PASS` in `.env`. The page shows orders & reservations as the
voice agent creates them, so the restaurant can see what the bot took in real time.

## Going further (post-traction)
- Swap `app/store.py` for Supabase (same function signatures).
- Multi-tenant: add `restaurant_id` to every record; one assistant per restaurant.
- Kitchen push: webhook order -> POS / Slack / printer.
- Human handoff tool; call analytics dashboard; IVR menu.
