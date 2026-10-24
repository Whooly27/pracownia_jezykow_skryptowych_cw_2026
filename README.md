# Pracownia Języków Skryptowych — 2026

Monorepo for the course project: a **Django + PostgreSQL** API and a **React 19 + TypeScript** SPA, each with its own CI/CD pipeline.

[![backend](https://github.com/Whooly27/pracownia_jezykow_skryptowych_cw_2026/actions/workflows/backend.yml/badge.svg)](https://github.com/Whooly27/pracownia_jezykow_skryptowych_cw_2026/actions/workflows/backend.yml)
[![frontend](https://github.com/Whooly27/pracownia_jezykow_skryptowych_cw_2026/actions/workflows/frontend.yml/badge.svg)](https://github.com/Whooly27/pracownia_jezykow_skryptowych_cw_2026/actions/workflows/frontend.yml)

## Repository layout

```
.
├── apps/
│   ├── backend/          # Django 5.2 LTS · Python 3.13 · uv · PostgreSQL 17
│   └── frontend/         # React 19 · TypeScript · Vite · React Router · Vitest
├── docs/
│   └── adr/              # Architecture Decision Records
├── .github/
│   ├── workflows/
│   │   ├── backend.yml        # Backend CI/CD (runs only on apps/backend/** changes)
│   │   ├── frontend.yml       # Frontend CI/CD (runs only on apps/frontend/** changes)
│   │   └── _docker-image.yml  # Reusable: build & publish images to GHCR
│   ├── dependabot.yml
│   ├── CODEOWNERS
│   └── pull_request_template.md
├── docker-compose.yml    # Local full stack: db + backend + frontend
└── Makefile              # Unified dev commands (`make help`)
```

## Quick start

### Option A: everything in Docker

```sh
cp .env.example .env
docker compose up --build
# SPA:  http://localhost:8080
# API:  http://localhost:8000/api/health/
```

### Option B: native dev with hot reload

Requires [uv](https://docs.astral.sh/uv/), Node.js 24 (`.nvmrc`), and Docker for Postgres.

```sh
make db                # Postgres in Docker (host ports are configurable in .env)
make install           # uv sync + npm ci
cp apps/backend/.env.example apps/backend/.env
cd apps/backend && uv run python manage.py migrate && cd -
make backend-dev       # http://localhost:8000
make frontend-dev      # http://localhost:5173 (proxies /api to the backend)
```

Run `make help` for lint, type-check and test targets.

## CI/CD

| Trigger                      | What runs                                                                 |
| ---------------------------- | ------------------------------------------------------------------------- |
| Pull request                 | Lint, type-check, tests, Docker build (no push), for the changed app only |
| Push to `main`               | Same as above, then push image to GHCR tagged `sha-…`, `main`, `latest`   |
| Tag `v*`                     | Same as above, plus semver image tag                                      |

Images: `ghcr.io/whooly27/pracownia_jezykow_skryptowych_cw_2026/{backend,frontend}`.

Deploying those images to a runtime environment is intentionally left out until a target platform is chosen.

## Conventions

- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/) with app scope, e.g. `feat(backend): add courses API`.
- **Branches:** short-lived feature branches off `main`, merged via PR.
- **Decisions:** significant architectural choices get an ADR in `docs/adr/`.
