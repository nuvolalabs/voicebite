"""Data backend. Auto-selects Supabase when SUPABASE_URL + SUPABASE_SERVICE_KEY
are set, otherwise falls back to an in-memory store. Both implement the same
function surface so the route handlers and admin never change.

Supabase tables (see supabase_schema.sql):
  menu         (id text pk, name text, category text, price numeric, options jsonb, option_prices jsonb)
  orders       (order_id text pk, customer_name text, phone text, items jsonb,
                total numeric, status text, payment_link text, created_at timestamptz)
  reservations (reservation_id text pk, customer_name text, phone text, party_size int,
                date text, time text, status text, created_at timestamptz)
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional

from app import config
from app.models import TakeoutOrder, Reservation, OrderItem, OrderStatus


# ----------------------------------------------------------------------------
# In-memory backend
# ----------------------------------------------------------------------------
class MemoryBackend:
    def __init__(self, seed: dict):
        self.MENU = dict(seed)
        self.ORDERS: dict[str, TakeoutOrder] = {}
        self.RESERVATIONS: dict[str, Reservation] = {}

    # menu reads
    def get_menu(self, category=None):
        items = list(self.MENU.values())
        if category:
            items = [i for i in items if i["category"].lower() == category.lower()]
        return items

    def lookup_item(self, item_id):
        return self.MENU.get(item_id)

    def add_menu_item(self, name, category, price):
        mid = self._next_id()
        self.MENU[mid] = {"id": mid, "name": name, "category": category, "price": float(price)}
        return mid

    def update_menu_item(self, item_id, name, category, price):
        if item_id not in self.MENU:
            return None
        self.MENU[item_id] = {"id": item_id, "name": name, "category": category, "price": float(price)}
        return self.MENU[item_id]

    def delete_menu_item(self, item_id):
        return self.MENU.pop(item_id, None) is not None

    # orders
    def create_order(self, order: TakeoutOrder):
        self.ORDERS[order.order_id] = order
        return order

    def get_order(self, order_id):
        return self.ORDERS.get(order_id)

    def update_order(self, order: TakeoutOrder):
        self.ORDERS[order.order_id] = order

    def list_orders(self):
        return list(self.ORDERS.values())

    # reservations
    def create_reservation(self, res: Reservation):
        self.RESERVATIONS[res.reservation_id] = res
        return res

    def list_reservations(self):
        return list(self.RESERVATIONS.values())

    def _next_id(self):
        n = 1
        while f"x{n}" in self.MENU:
            n += 1
        return f"x{n}"


# ----------------------------------------------------------------------------
# Supabase backend
# ----------------------------------------------------------------------------
class SupabaseBackend:
    def __init__(self, url: str, key: str):
        from supabase import create_client
        self.sb = create_client(url, key)

    def get_menu(self, category=None):
        q = self.sb.table("menu").select("*")
        if category:
            q = q.eq("category", category.lower())
        rows = q.execute().data or []
        return rows

    def lookup_item(self, item_id):
        rows = self.sb.table("menu").select("*").eq("id", item_id).execute().data or []
        return rows[0] if rows else None

    def add_menu_item(self, name, category, price):
        mid = "x" + uuid.uuid4().hex[:8]
        row = {"id": mid, "name": name, "category": category, "price": float(price),
               "options": [], "option_prices": {}}
        self.sb.table("menu").insert(row).execute()
        return mid

    def update_menu_item(self, item_id, name, category, price):
        rows = self.sb.table("menu").update(
            {"name": name, "category": category, "price": float(price)}
        ).eq("id", item_id).execute().data
        return rows[0] if rows else None

    def delete_menu_item(self, item_id):
        res = self.sb.table("menu").delete().eq("id", item_id).execute()
        return bool(res.data)

    def create_order(self, order: TakeoutOrder):
        row = {
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "phone": order.phone,
            "items": [i.model_dump() for i in order.items],
            "total": order.total,
            "status": order.status.value,
            "payment_link": order.payment_link,
            "created_at": order.created_at,
        }
        self.sb.table("orders").insert(row).execute()
        return order

    def get_order(self, order_id):
        rows = self.sb.table("orders").select("*").eq("order_id", order_id).execute().data or []
        return _row_to_order(rows[0]) if rows else None

    def update_order(self, order: TakeoutOrder):
        self.sb.table("orders").update({
            "status": order.status.value,
            "payment_link": order.payment_link,
            "items": [i.model_dump() for i in order.items],
            "total": order.total,
        }).eq("order_id", order.order_id).execute()
        return order

    def list_orders(self):
        rows = self.sb.table("orders").select("*").order("created_at", desc=False).execute().data or []
        return [_row_to_order(r) for r in rows]

    def create_reservation(self, res: Reservation):
        row = {
            "reservation_id": res.reservation_id,
            "customer_name": res.customer_name,
            "phone": res.phone,
            "party_size": res.party_size,
            "date": res.date,
            "time": res.time,
            "status": res.status,
            "created_at": res.created_at,
        }
        self.sb.table("reservations").insert(row).execute()
        return res

    def list_reservations(self):
        rows = self.sb.table("reservations").select("*").order("created_at", desc=False).execute().data or []
        return [_row_to_res(r) for r in rows]


def _row_to_order(r: dict) -> TakeoutOrder:
    return TakeoutOrder(
        order_id=r["order_id"],
        customer_name=r["customer_name"],
        phone=r["phone"],
        items=[OrderItem(**i) for i in r.get("items", [])],
        total=float(r["total"]),
        status=OrderStatus(r.get("status", "created")),
        payment_link=r.get("payment_link"),
        created_at=r.get("created_at", ""),
    )


def _row_to_res(r: dict) -> Reservation:
    return Reservation(
        reservation_id=r["reservation_id"],
        customer_name=r["customer_name"],
        phone=r["phone"],
        party_size=int(r["party_size"]),
        date=r["date"],
        time=r["time"],
        status=r.get("status", "confirmed"),
        created_at=r.get("created_at", ""),
    )


# ----------------------------------------------------------------------------
# Seed menu (Hakka Legend — Markham) shared by the memory backend
# ----------------------------------------------------------------------------
def _seed_menu() -> dict:
    from app import seed
    return seed.MENU


# ----------------------------------------------------------------------------
# Public facade — same function names the rest of the app already calls
# ----------------------------------------------------------------------------
_backend: Optional[object] = None


def _get_backend():
    global _backend
    if _backend is None:
        if config.using_supabase():
            _backend = SupabaseBackend(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
        else:
            _backend = MemoryBackend(_seed_menu())
    return _backend


# convenience re-exports used elsewhere
def get_menu(category=None):
    return _get_backend().get_menu(category)

def lookup_item(item_id):
    return _get_backend().lookup_item(item_id)

def add_menu_item(name, category, price):
    return _get_backend().add_menu_item(name, category, price)

def update_menu_item(item_id, name, category, price):
    return _get_backend().update_menu_item(item_id, name, category, price)

def delete_menu_item(item_id):
    return _get_backend().delete_menu_item(item_id)

def create_order(customer_name, phone, items):
    order = _build_order(customer_name, phone, items)
    return _get_backend().create_order(order)

def get_order(order_id):
    return _get_backend().get_order(order_id)

def update_order(order: TakeoutOrder):
    return _get_backend().update_order(order)

def set_order_paid(order_id: str, payment_link: str | None = None) -> bool:
    order = get_order(order_id)
    if not order:
        return False
    order.status = OrderStatus.PAID
    if payment_link:
        order.payment_link = payment_link
    update_order(order)
    return True

def create_reservation(customer_name, phone, party_size, date, time):
    res = Reservation(
        reservation_id="res_" + uuid.uuid4().hex[:10],
        customer_name=customer_name,
        phone=phone,
        party_size=party_size,
        date=date,
        time=time,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    return _get_backend().create_reservation(res)

def list_orders():
    return _get_backend().list_orders()

def list_reservations():
    return _get_backend().list_reservations()


def _resolve_price(item: dict, option: Optional[str]) -> float:
    if option and item.get("option_prices"):
        return float(item["option_prices"].get(option.lower(), item["price"]))
    return float(item["price"])


def _build_order(customer_name: str, phone: str, items: list[OrderItem]) -> TakeoutOrder:
    order_id = "ord_" + uuid.uuid4().hex[:10]
    total = 0.0
    for it in items:
        meta = lookup_item(it.item_id)
        if meta:
            it.name = meta["name"]
            it.unit_price = _resolve_price(meta, it.option)
            total += it.unit_price * it.quantity
        else:
            total += it.unit_price * it.quantity
    return TakeoutOrder(
        order_id=order_id,
        customer_name=customer_name,
        phone=phone,
        items=items,
        total=round(total, 2),
        status=OrderStatus.CREATED,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
