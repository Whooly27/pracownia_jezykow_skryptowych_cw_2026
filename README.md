# Pracownia Języków Skryptowych — 2026

Monorepo for the course project: a **Django + PostgreSQL** API and a **Vue 3 + TypeScript** SPA, each with its own CI/CD pipeline.

[![backend](https://github.com/Whooly27/pracownia_jezykow_skryptowych_cw_2026/actions/workflows/backend.yml/badge.svg)](https://github.com/Whooly27/pracownia_jezykow_skryptowych_cw_2026/actions/workflows/backend.yml)
[![frontend](https://github.com/Whooly27/pracownia_jezykow_skryptowych_cw_2026/actions/workflows/frontend.yml/badge.svg)](https://github.com/Whooly27/pracownia_jezykow_skryptowych_cw_2026/actions/workflows/frontend.yml)

## Repository layout

```
.
├── apps/
│   ├── backend/          # Django 5.2 LTS · Python 3.13 · uv · PostgreSQL 17
│   └── frontend/         # Vue 3 · TypeScript · Vite · Pinia · Vue Router · Vitest
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
| Push to `main`               | Same as above, then push image to GHCR and deploy to Vercel               |
| Tag `v*`                     | Same as above (minus deploy), plus semver image tag                       |

Images: `ghcr.io/whooly27/pracownia_jezykow_skryptowych_cw_2026/{backend,frontend}`.

### Deployment (Vercel + Neon Postgres)

Both apps deploy from GitHub Actions; all runtime configuration lives in GitHub, not in the Vercel dashboard.

- **backend:** runs `migrate` against the production database, then deploys Django as a Vercel Python function with env vars passed via `vercel deploy --env`.
- **frontend:** deploys the built `dist/` as static files; `/api/*` is rewritten to the backend, so the SPA keeps using same-origin `/api` like it does behind nginx.

One-time setup:

1. Create a Postgres database on [Neon](https://neon.tech) and copy the **pooled** connection string (host contains `-pooler`, ends with `?sslmode=require`).
2. Create two Vercel projects without connecting Git (Git deploys are disabled anyway), e.g. `vercel link` in `apps/backend` and `apps/frontend`. Leave **Root Directory** empty. Note the `orgId`/`projectId` from each `.vercel/project.json`.
3. Create a Vercel access token (Account Settings → Tokens).
4. In GitHub → Settings → Environments, create `production` and add:

   | Secret                       | Value                                       |
   | ---------------------------- | ------------------------------------------- |
   | `VERCEL_TOKEN`               | token from step 3                           |
   | `VERCEL_ORG_ID`              | `orgId`                                     |
   | `VERCEL_BACKEND_PROJECT_ID`  | backend `projectId`                         |
   | `VERCEL_FRONTEND_PROJECT_ID` | frontend `projectId`                        |
   | `DJANGO_SECRET_KEY`          | long random string                          |
   | `DATABASE_URL`               | Neon connection string from step 1          |

   | Variable                      | Example                                |
   | ----------------------------- | -------------------------------------- |
   | `BACKEND_URL`                 | `https://psj-backend.vercel.app`       |
   | `FRONTEND_URL`                | `https://psj-frontend.vercel.app`      |
   | `DJANGO_ALLOWED_HOSTS`        | `psj-backend.vercel.app`               |
   | `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://psj-backend.vercel.app`       |

Changing a secret or variable takes effect on the next deploy (re-run the workflow via **Run workflow**).

## Conventions

- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/) with app scope, e.g. `feat(backend): add courses API`.
- **Branches:** short-lived feature branches off `main`, merged via PR.
- **Decisions:** significant architectural choices get an ADR in `docs/adr/`.
