"""Admin page + JSON API. Served by the same FastAPI app.

Routes:
  GET  /admin            -> the HTML page (Basic auth)
  GET  /admin/api/menu   -> current menu
  POST /admin/api/menu   -> add item  {name, category, price}
  PUT  /admin/api/menu   -> update item {id, name, category, price}
  DEL  /admin/api/menu   -> delete item {id}
  GET  /admin/api/orders -> recent orders
  GET  /admin/api/reservations -> recent reservations
"""
from __future__ import annotations
import os
from fastapi import APIRouter, Request, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from app import config, store

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBasic(auto_error=False)

# Minimal templating without extra deps: we render the page from a string.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _authenticate(creds: HTTPBasicCredentials | None):
    if creds is None or not (
        _constant_eq(creds.username, config.ADMIN_USER)
        and _constant_eq(creds.password, config.ADMIN_PASS)
    ):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )


def _constant_eq(a: str, b: str) -> bool:
    import hmac
    return hmac.compare_digest(a.encode(), b.encode())


@router.get("", response_class=HTMLResponse)
def admin_page(request: Request, creds: HTTPBasicCredentials | None = Depends(security)):
    _authenticate(creds)
    with open(os.path.join(_BASE_DIR, "admin_page.html")) as f:
        return HTMLResponse(f.read())


@router.get("/api/menu")
def api_menu(creds: HTTPBasicCredentials | None = Depends(security)):
    _authenticate(creds)
    return store.get_menu()


@router.post("/api/menu")
def api_menu_add(item: dict, creds: HTTPBasicCredentials | None = Depends(security)):
    _authenticate(creds)
    mid = store.add_menu_item(item["name"], item["category"], float(item["price"]))
    return {"id": mid, "ok": True}


@router.put("/api/menu")
def api_menu_update(item: dict, creds: HTTPBasicCredentials | None = Depends(security)):
    _authenticate(creds)
    res = store.update_menu_item(item["id"], item["name"], item["category"], float(item["price"]))
    if res is None:
        raise HTTPException(status_code=404, detail="item not found")
    return {"ok": True}


@router.delete("/api/menu")
def api_menu_delete(payload: dict, creds: HTTPBasicCredentials | None = Depends(security)):
    _authenticate(creds)
    ok = store.delete_menu_item(payload["id"])
    if not ok:
        raise HTTPException(status_code=404, detail="item not found")
    return {"ok": True}


@router.get("/api/orders")
def api_orders(creds: HTTPBasicCredentials | None = Depends(security)):
    _authenticate(creds)
    return [o.model_dump() for o in store.list_orders()]


@router.get("/api/reservations")
def api_reservations(creds: HTTPBasicCredentials | None = Depends(security)):
    _authenticate(creds)
    return [r.model_dump() for r in store.list_reservations()]
