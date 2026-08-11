"""Import/sync vapi_assistant.prod.json into Vapi via the REST API.

Requires VAPI_API_KEY in .env (Vapi private key — your account issues a UUID,
NOT the pk_ format; it's the key from vapi.ai -> Settings -> API Keys).

What this does:
- PATCHES the existing assistant (by id in vapi_assistant.prod.json's
  "_assistant_id") OR creates one if missing.
- Uses the CURRENT Vapi schema: tools are type "function" under model.tools,
  and the tool-call HTTP endpoint is set via assistant.server.url (a single
  dispatcher route on the FastAPI server at /vapi/tool).

Run:
    source venv/bin/activate
    python scripts/import_vapi_assistant.py
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
import urllib.error

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_API_KEY")
if not API_KEY:
    print("ERROR: set VAPI_API_KEY in .env (Vapi private key).")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "..", "vapi_assistant.prod.json")
with open(JSON_PATH) as f:
    assistant = json.load(f)

AID = assistant.pop("_assistant_id", None)  # our own extension; not sent to Vapi
BASE = "https://api.vapi.ai/assistant"


def _req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }, method=method)
    return urllib.request.urlopen(r, timeout=30)


try:
    if AID:
        with _req("PATCH", f"{BASE}/{AID}", assistant) as resp:
            body = json.loads(resp.read())
        print("PATCHED assistant:", body.get("id"))
    else:
        with _req("POST", BASE, assistant) as resp:
            body = json.loads(resp.read())
        print("CREATED assistant:", body.get("id"))
        print("Add '_assistant_id':", repr(body.get("id")), "to vapi_assistant.prod.json for future syncs.")
    print("tools:", [t.get("function", {}).get("name") for t in body.get("model", {}).get("tools", [])])
    print("server.url:", (body.get("server") or {}).get("url"))
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()}")
    sys.exit(1)
