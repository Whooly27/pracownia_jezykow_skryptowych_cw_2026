# Backend

Django 5.2 (LTS) application backed by PostgreSQL. Dependencies are managed with [uv](https://docs.astral.sh/uv/).

## Prerequisites

- Python 3.13 (uv will install it automatically)
- uv
- PostgreSQL 17 (or run `docker compose up -d db` from the repo root)

## Getting started

```sh
uv sync                          # create .venv and install all deps
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver   # http://localhost:8000/api/health/
```

## Common tasks

| Command                                                | Purpose                       |
| ------------------------------------------------------ | ----------------------------- |
| `uv run pytest`                                        | Run tests (needs Postgres)    |
| `uv run ruff check . && uv run ruff format --check .`  | Lint and verify formatting    |
| `uv run mypy .`                                        | Static type checking          |
| `uv run python manage.py makemigrations --check`       | Fail if migrations are missing|

## Layout

```
config/            # Project wiring: settings, root URLconf, WSGI/ASGI
└── settings/
    ├── base.py        # Shared settings, read from environment
    ├── local.py       # Developer machines
    ├── test.py        # pytest
    └── production.py  # Hardened, container runtime
apps/              # Django apps, one per bounded context
└── core/          # Cross-cutting concerns (health check, ...)
```

New domain apps go under `apps/<name>/` and are registered in `LOCAL_APPS` in `config/settings/base.py`.

## Configuration

All configuration is read from environment variables (12-factor). See `.env.example` for the full list.
