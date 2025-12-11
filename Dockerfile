FROM python:3.11-slim AS deps

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip wheel --wheel-dir=/app/wheels -r requirements.txt

FROM deps AS builder

COPY . .

FROM python:3.11-slim AS runner

RUN useradd -m appuser
USER appuser

WORKDIR /app/src

COPY --from=deps /app/wheels /app/wheels
COPY --from=deps /app/requirements.txt ../requirements.txt
COPY . /app

RUN pip install --no-cache-dir --find-links=/app/wheels -r ../requirements.txt

CMD ["python", "main.py"]
