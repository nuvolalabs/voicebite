"""FastAPI backend for the restaurant voice agent (Vapi tool server).

Vapi calls these endpoints as 'tool' functions during a call. Each returns a
plain dict/string that Vapi reads back to the LLM so it can speak to the caller.
"""
from __future__ import annotations
import hmac
import hashlib
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import config, db as store, payments, restaurant
from app.admin import router as admin_router
from app.models import (
    GetMenuRequest, CreateOrderRequest, CreateReservationRequest, SendPaymentLinkRequest,
    OrderItem, OrderStatus,
)

app = FastAPI(title="Restaurant Voice Agent API", version="0.1.0")
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _verify_vapi(secret_header: str | None, raw_body: bytes) -> None:
    """Vapi signs tool calls with X-Vapi-Secret when configured. Optional in MVP."""
    if not config.VAPI_SECRET:
        return
    if secret_header != config.VAPI_SECRET:
        raise HTTPException(status_code=401, detail="Invalid Vapi secret")


@app.get("/")
def root():
    return {"status": "ok", "service": "restaurant-voice-agent"}


@app.get("/health")
def health():
    return {"status": "ok", "configured": config.is_configured(),
            "public_base_url": config.PUBLIC_BASE_URL or "(unset)"}


@app.get("/restaurant")
def restaurant_info():
    return restaurant.RESTAURANT


@app.post("/tools/get_menu")
async def get_menu(req: GetMenuRequest, request: Request,
                   x_vapi_secret: str | None = Header(None)):
    _verify_vapi(x_vapi_secret, await request.body())
    items = store.get_menu(req.category)
    cats: dict[str, list[str]] = {}
    for it in items:
        label = it["name"]
        if it.get("options"):
            label += f" ({'/'.join(it['options'][:4])}{'...' if len(it['options']) > 4 else ''})"
        cats.setdefault(it["category"], []).append(f"{label} ${it['price']:.2f}")
    lines = [f"{cat.title()}: " + ", ".join(v) for cat, v in cats.items()]
    return {"menu": items, "summary": "Menu. " + " | ".join(lines)}


@app.post("/tools/create_order")
async def create_order(req: CreateOrderRequest, request: Request,
                       x_vapi_secret: str | None = Header(None)):
    _verify_vapi(x_vapi_secret, await request.body())
    order = store.create_order(req.customer_name, req.phone, req.items)
    return {
        "order_id": order.order_id,
        "total": order.total,
        "item_count": len(order.items),
        "message": f"Order created for {req.customer_name}, total ${order.total:.2f}.",
    }


@app.post("/tools/create_reservation")
async def create_reservation(req: CreateReservationRequest, request: Request,
                             x_vapi_secret: str | None = Header(None)):
    _verify_vapi(x_vapi_secret, await request.body())
    res = store.create_reservation(
        req.customer_name, req.phone, req.party_size, req.date, req.time)
    return {
        "reservation_id": res.reservation_id,
        "message": f"Table for {req.party_size} on {req.date} at {req.time} confirmed for {req.customer_name}.",
    }


@app.post("/tools/send_payment_link")
async def send_payment_link(req: SendPaymentLinkRequest, request: Request,
                            x_vapi_secret: str | None = Header(None)):
    _verify_vapi(x_vapi_secret, await request.body())
    link = payments.create_payment_link(req.amount, req.order_id, req.customer_name)
    sent = payments.send_sms(req.phone, f"Hi {req.customer_name}, pay for your order here: {link}")

    # Persist status so the admin/Stripe webhook can track payment.
    order = store.get_order(req.order_id) if req.order_id else None
    if order is not None:
        from app.models import OrderStatus
        order.status = OrderStatus.PAYMENT_SENT
        order.payment_link = link
        store.update_order(order)

    return {
        "payment_link": link,
        "sms_sent": sent,
        "message": f"Payment link sent to {req.phone}.",
    }


@app.post("/vapi/tool")
async def vapi_tool(request: Request):
    """Vapi 'function' tool dispatcher.

    When an assistant uses `type: "function"` tools, Vapi POSTs ALL tool calls
    to `assistant.server.url` (a single endpoint) with a function-call message,
    then expects `{"results":[{"toolCallId", "result"}]}` back. This route
    extracts the function name + args and reuses the same logic as the
    per-tool /tools/* endpoints.
    """
    import json as _json

    raw = await request.body()
    try:
        payload = _json.loads(raw or b"{}")
    except Exception:
        payload = {}

    # Vapi sends either a server-message envelope or a bare function-call body.
    msg = payload.get("message", payload)
    if isinstance(msg, dict) and msg.get("type") == "function-call":
        fc = msg.get("functionCall", {})
    elif "functionCall" in payload:
        fc = payload["functionCall"]
    elif "function" in payload and isinstance(payload["function"], dict):
        fc = payload["function"]
    else:
        # bare body: {name:..., parameters:...}
        fc = {"name": payload.get("name"), "parameters": payload.get("parameters", {})}
    name = fc.get("name")
    tool_call_id = fc.get("toolCallId") or (msg.get("toolCallId") if isinstance(msg, dict) else None)
    args = fc.get("parameters") or fc.get("arguments") or {}

    # Vapi sometimes serializes arguments as a JSON string.
    if isinstance(args, str):
        try:
            args = _json.loads(args)
        except Exception:
            args = {}

    try:
        if name == "get_menu":
            items = store.get_menu(args.get("category"))
            result = {"menu": items, "count": len(items)}
        elif name == "create_order":
            order = store.create_order(
                args["customer_name"], args["phone"],
                [OrderItem(**i) for i in args["items"]],
            )
            result = {"order_id": order.order_id, "total": order.total,
                      "item_count": len(order.items),
                      "message": f"Order created for {args['customer_name']}, total ${order.total:.2f}."}
        elif name == "create_reservation":
            res = store.create_reservation(
                args["customer_name"], args["phone"], args["party_size"],
                args["date"], args["time"])
            result = {"reservation_id": res.reservation_id,
                      "message": f"Table for {args['party_size']} on {args['date']} at {args['time']} confirmed for {args['customer_name']}."}
        elif name == "send_payment_link":
            order_id = args.get("order_id") or ""
            link = payments.create_payment_link(args["amount"], order_id, args["customer_name"])
            sent = payments.send_sms(args["phone"], f"Hi {args['customer_name']}, pay here: {link}")
            order = store.get_order(order_id) if order_id else None
            if order is not None:
                order.status = OrderStatus.PAYMENT_SENT
                order.payment_link = link
                store.update_order(order)
            result = {"payment_link": link, "sms_sent": sent,
                      "message": f"Payment link sent to {args['phone']}."}
        else:
            result = {"error": f"Unknown tool: {name}"}
    except Exception as e:  # noqa: BLE001
        result = {"error": str(e)}

    if tool_call_id:
        return {"results": [{"toolCallId": tool_call_id, "result": result}]}
    return result


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Mark an order PAID when its Stripe Payment Link is completed.

    Wire this in the Stripe dashboard: Webhooks -> add endpoint
    <PUBLIC_BASE_URL>/stripe/webhook, listen for `checkout.session.completed`
    (Payment Links emit that event). Set STRIPE_WEBHOOK_SECRET in .env to verify.
    """
    import stripe as _stripe
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature", "")

    if config.STRIPE_WEBHOOK_SECRET:
        try:
            event = _stripe.Webhook.construct_event(
                payload, sig, config.STRIPE_WEBHOOK_SECRET)
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")
    else:
        import json
        event = json.loads(payload or b"{}")

    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = (session.get("metadata") or {}).get("order_id")
        if order_id and store.set_order_paid(order_id, session.get("url")):
            return {"received": True, "order_id": order_id, "status": "paid"}

    return {"received": True}

