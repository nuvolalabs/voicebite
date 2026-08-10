FROM python:3.12-slim

WORKDIR /app

# uv is the fastest installer; fallback to pip if absent
RUN pip install --no-cache-dir uv || true

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt || pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
# Honor Railway's injected $PORT so the healthcheck probe hits the right port.
ENV PORT=8000
CMD uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
