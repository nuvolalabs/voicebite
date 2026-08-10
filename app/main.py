"""FastAPI backend for the restaurant voice agent (Vapi tool server).

Vapi calls these endpoints as 'tool' functions during a call. Each returns a
plain dict/string that Vapi reads back to the LLM so it can speak to the caller.
"""
from __future__ import annotations
import hmac
import hashlib
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import config, store, payments, restaurant
from app.admin import router as admin_router
from app.models import (
    GetMenuRequest, CreateOrderRequest, CreateReservationRequest, SendPaymentLinkRequest,
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
    link = payments.create_payment_link(req.amount, "", req.customer_name)
    sent = payments.send_sms(req.phone, f"Hi {req.customer_name}, pay for your order here: {link}")
    return {
        "payment_link": link,
        "sms_sent": sent,
        "message": f"Payment link sent to {req.phone}.",
    }
