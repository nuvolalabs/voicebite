FROM python:3.12-slim

WORKDIR /app

# uv is the fastest installer; fallback to pip if absent
RUN pip install --no-cache-dir uv || true

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt || pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
# Railway injects PORT at runtime. Use a shell form so $PORT expands; fall back
# to 8000 if unset. (A bare CMD "uvicorn ... --port ${PORT}" does NOT expand
# the var and crashes with "'$PORT' is not a valid integer".)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
