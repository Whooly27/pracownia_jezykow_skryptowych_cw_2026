# Frontend

React 19 + TypeScript SPA built with Vite. Routing with React Router, authentication via Amazon Cognito (`react-oidc-context`), unit tests with Vitest + React Testing Library.

## Prerequisites

- Node.js 24 (see `.nvmrc` at repo root)

## Getting started

```sh
npm ci
cp .env.example .env.local   # API proxy target + Cognito (OIDC) settings
npm run dev                  # http://localhost:5173, proxies /api -> backend
```

## Scripts

| Command                | Purpose                                   |
| ---------------------- | ----------------------------------------- |
| `npm run dev`          | Start the dev server with HMR             |
| `npm run build`        | Type-check and build for production       |
| `npm run test:unit`    | Run Vitest in watch mode                  |
| `npm run test:ci`      | Run Vitest once (used in CI)              |
| `npm run lint`         | Lint and auto-fix (oxlint + ESLint)       |
| `npm run lint:check`   | Lint without fixing (used in CI)          |
| `npm run format`       | Format sources with Prettier              |
| `npm run format:check` | Verify formatting (used in CI)            |

## Layout

```
src/
├── api/        # HTTP client and typed endpoint wrappers
├── auth/       # Cognito OIDC configuration for <AuthProvider>
├── hooks/      # Data-fetching / state hooks
├── router/     # React Router configuration
├── views/      # Route-level components
└── __tests__/  # Unit tests
```

## Container image

`Dockerfile` builds static assets and serves them via unprivileged nginx on port 8080. `nginx.conf` proxies `/api/` to the `backend` service, so the SPA and API share an origin (no CORS needed).
