# DynoDoc API — FastAPI on uv / Python 3.13.
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Settle the day in IST so the nightly leaderboard payout aligns to IST midnight.
    TZ=Asia/Kolkata

# uv (the package manager) — copied from the official distroless image.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (cached layer) using the locked versions.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Then the application code.
COPY . .
RUN uv sync --frozen --no-dev

EXPOSE 8000

# Apply migrations, then serve. `alembic upgrade head` is idempotent (a no-op
# when already current), so it's safe on every (cold) start — which matters on
# Render's free plan, where pre-deploy commands aren't available. Render injects
# $PORT; shell form lets it (and &&) expand.
CMD uv run alembic upgrade head && uv run uvicorn app.runtime.application:app --host 0.0.0.0 --port ${PORT:-8000}
