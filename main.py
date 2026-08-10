# Thin shim so `uvicorn main:app` (and auto-detecting tools) resolve to the
# real app package. Railway uses the explicit `app.main:app` from railway.toml.
from app.main import app

__all__ = ["app"]
