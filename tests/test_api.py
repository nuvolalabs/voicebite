"""Smoke tests for the voice-agent backend (in-memory mode, no external creds)."""
import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Force in-memory backend (no Supabase env) before importing the app.
    import os
    os.environ.pop("SUPABASE_URL", None)
    os.environ.pop("SUPABASE_SERVICE_KEY", None)
    import app.db as db
    import app.config as config
    db._backend = None  # reset cached backend
    assert not config.using_supabase()
    from app.main import app
    importlib.reload  # noqa
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_menu_seeded_and_categorized(client):
    r = client.post("/tools/get_menu", json={})
    body = r.json()
    assert r.status_code == 200
    assert len(body["menu"]) >= 100
    cats = {i["category"] for i in body["menu"]}
    assert {"appetizers", "noodles", "rice", "soups", "chicken"} <= cats


def test_order_with_protein_option_pricing(client):
    # Hakka Noodle seafood option = $16.00
    r = client.post("/tools/create_order", json={
        "customer_name": "Test", "phone": "+14165551234",
        "items": [{"item_id": "n1", "option": "seafood", "quantity": 1}]})
    assert r.status_code == 200
    assert r.json()["total"] == 16.0


def test_order_with_base_protein_pricing(client):
    # Hakka Noodle chicken = base $14.00
    r = client.post("/tools/create_order", json={
        "customer_name": "Test", "phone": "+14165551234",
        "items": [{"item_id": "n1", "option": "chicken", "quantity": 2}]})
    assert r.json()["total"] == 28.0


def test_soup_size_pricing(client):
    # Chicken Hot & Sour Soup medium = $9.99, qty 2 -> 19.98
    r = client.post("/tools/create_order", json={
        "customer_name": "Test", "phone": "+14165551234",
        "items": [{"item_id": "s3", "option": "medium", "quantity": 2}]})
    assert r.json()["total"] == 19.98


def test_reservation_created(client):
    r = client.post("/tools/create_reservation", json={
        "customer_name": "Test", "phone": "+14165551234",
        "party_size": 3, "date": "2026-08-15", "time": "19:00"})
    assert r.status_code == 200
    assert "confirmed" in r.json()["message"]


def test_admin_auth_enforced(client):
    # No creds -> 401
    assert client.get("/admin").status_code == 401
    # Wrong creds -> 401
    assert client.get("/admin", auth=("admin", "wrong")).status_code == 401


def test_admin_add_and_list_menu(client):
    r = client.post("/admin/api/menu", auth=("admin", "secret"),
                    json={"name": "Test Item", "category": "desserts", "price": 4.0})
    assert r.status_code == 200
    mid = r.json()["id"]
    lst = client.get("/admin/api/menu", auth=("admin", "secret")).json()
    assert any(i["id"] == mid for i in lst)


def test_stripe_webhook_marks_paid(client):
    # Create an order, send link (persists PAYMENT_SENT), then simulate webhook.
    o = client.post("/tools/create_order", json={
        "customer_name": "Web", "phone": "+14165551234",
        "items": [{"item_id": "r9", "quantity": 1}]}).json()  # steamed rice $2.50
    oid = o["order_id"]
    client.post("/tools/send_payment_link", json={
        "order_id": oid, "customer_name": "Web", "phone": "+14165551234", "amount": 2.5})

    wh = {
        "type": "checkout.session.completed",
        "data": {"object": {"metadata": {"order_id": oid}, "url": "https://pay.stripe/xyz"}},
    }
    r = client.post("/stripe/webhook", json=wh)
    assert r.status_code == 200
    assert r.json().get("status") == "paid"
