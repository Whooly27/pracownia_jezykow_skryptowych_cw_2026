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

## Upload locally

File bytes never pass through the API. `POST /api/v1/uploads` reserves a name and returns a signed
`put_url`; the browser PUTs the bytes there; `POST /api/v1/uploads/{id}/complete` checks they arrived
and makes the file visible. In development the signed URL points back at this server
(`/api/v1/_blob/...`), which stores the bytes under `BLOB_ROOT` (default `blobdata/`, git-ignored)
as a stand-in for Vercel Blob. Swap `STORAGE_BACKEND` for a real client later; the views don't change.

The migrations were regenerated on 7 Nov 2026 (flat files, no folders). A database created before
that needs a reset: `docker compose down -v db && docker compose up -d db`, then `migrate`.

Sign-in is not wired yet, so for a manual run log in at `/admin/` with a superuser
(`uv run python manage.py createsuperuser`) and reuse the session cookie:

```sh
curl -s -c jar -b jar http://localhost:8000/admin/login/ -o /dev/null
CSRF=$(grep csrftoken jar | cut -f7)
curl -s -c jar -b jar -X POST http://localhost:8000/admin/login/ \
  -d "csrfmiddlewaretoken=$CSRF&username=you@example.com&password=secret" -o /dev/null

curl -s -b jar -X POST http://localhost:8000/api/v1/uploads -H 'content-type: application/json' \
  -d '{"name":"hello.txt","size_bytes":6,"mime_type":"text/plain"}'
# one file per request; take put_url and id from the answer
curl -s -X PUT "http://localhost:8000<put_url>" -H 'content-type: text/plain' --data-binary 'hello!'
curl -s -b jar -X POST http://localhost:8000/api/v1/uploads/<id>/complete
```

Replace a file's contents the same way, starting with `POST /api/v1/files/{id}/replace`
(`{"size_bytes": ..., "mime_type": ...}`) instead of `POST /api/v1/uploads`.

## Layout

```
config/            # Project wiring: settings, root URLconf, WSGI/ASGI
└── settings/
    ├── base.py        # Shared settings, read from environment
    ├── local.py       # Developer machines
    ├── test.py        # pytest
    └── production.py  # Hardened, container runtime
apps/              # Django apps, one per bounded context
├── core/          # Health check, API envelope helpers
├── accounts/      # User
├── files/         # File and its JSON shape
├── sharing/       # Permissions, share links, grants, access_for
└── uploads/       # Upload policy, storage, upload endpoints
```

New domain apps go under `apps/<name>/` and are registered in `LOCAL_APPS` in `config/settings/base.py`.

## Configuration

All configuration is read from environment variables (12-factor). See `.env.example` for the full list.
