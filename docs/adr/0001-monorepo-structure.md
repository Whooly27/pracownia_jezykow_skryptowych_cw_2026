# ADR 0001: Monorepo with independently built apps

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

The project has a Django backend and a Vue frontend. They change together often (API contract plus UI), but they use different toolchains (uv/Python vs npm/Node) and deploy as separate artifacts.

## Decision

- One repository, with applications under `apps/<name>/`. Each app is self-contained: its own dependency manifest, lockfile, Dockerfile and README. Nothing at the repo root is required to build an app.
- No cross-language monorepo tool (Nx, Turborepo, Bazel). With two apps, a root `Makefile` plus path-filtered GitHub Actions workflows gives the same "only build what changed" benefit without extra tooling.
- One CI workflow per app, triggered by `paths:` filters. Docker build and publish logic lives in a single reusable workflow (`_docker-image.yml`) so both apps share image conventions.
- Artifacts are container images in GHCR, tagged by commit SHA (immutable) and by branch, `latest` or semver (mutable).
- In the container setup, the SPA reaches the API via same-origin `/api` (nginx reverse proxy), and in development via the Vite proxy. This avoids CORS configuration entirely.

## Consequences

- Atomic PRs across backend and frontend are possible.
- Adding a third app means adding `apps/<new>/` plus a workflow that calls `_docker-image.yml`.
- Path filters mean a required status check may not run on PRs that don't touch that app. If branch protection is enabled, use an aggregate "CI passed" job or make checks conditional rather than required.
- If the number of apps or shared packages grows (e.g. a generated API client in `packages/`), revisit adopting a monorepo task runner.
