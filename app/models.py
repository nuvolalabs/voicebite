"""Pydantic models for menu, orders, reservations + Vapi tool payloads."""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class OrderItem(BaseModel):
    item_id: str
    name: Optional[str] = None     # filled from menu by the store
    option: Optional[str] = None    # e.g. "chicken", "medium", "spicy"
    quantity: int = 1
    notes: Optional[str] = None
    unit_price: float = 0.0         # filled from menu by the store


class OrderStatus(str, Enum):
    CREATED = "created"
    PAYMENT_SENT = "payment_sent"
    PAID = "paid"
    CANCELLED = "cancelled"


class TakeoutOrder(BaseModel):
    order_id: str
    customer_name: str
    phone: str
    items: list[OrderItem]
    total: float = 0.0
    status: OrderStatus = OrderStatus.CREATED
    payment_link: Optional[str] = None
    created_at: str = ""


class Reservation(BaseModel):
    reservation_id: str
    customer_name: str
    phone: str
    party_size: int
    date: str          # YYYY-MM-DD
    time: str          # HH:MM (24h)
    status: str = "confirmed"
    created_at: str = ""


# ---------- Vapi tool request bodies (Vapi posts these as JSON) ----------
class GetMenuRequest(BaseModel):
    category: Optional[str] = None


class CreateOrderRequest(BaseModel):
    customer_name: str
    phone: str
    items: list[OrderItem]


class CreateReservationRequest(BaseModel):
    customer_name: str
    phone: str
    party_size: int = Field(ge=1)
    date: str
    time: str


class SendPaymentLinkRequest(BaseModel):
    order_id: str
    customer_name: str
    phone: str
    amount: float
