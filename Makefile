# Developer entrypoints for the whole monorepo. Run `make help` to list targets.

BACKEND  := apps/backend
FRONTEND := apps/frontend

.DEFAULT_GOAL := help
.PHONY: help install db up down lint test typecheck build \
        backend-install backend-lint backend-test backend-typecheck backend-dev \
        frontend-install frontend-lint frontend-test frontend-typecheck frontend-build frontend-dev

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: backend-install frontend-install ## Install all dependencies
lint: backend-lint frontend-lint ## Lint everything
typecheck: backend-typecheck frontend-typecheck ## Type-check everything
test: backend-test frontend-test ## Run all tests
build: frontend-build ## Build production artifacts

db: ## Start only Postgres in the background
	docker compose up -d db

up: ## Build and start the full stack
	docker compose up --build

down: ## Stop the stack
	docker compose down

backend-install: ## Install backend deps
	cd $(BACKEND) && uv sync

backend-lint: ## Lint + format-check backend
	cd $(BACKEND) && uv run ruff check . && uv run ruff format --check .

backend-typecheck: ## Type-check backend
	cd $(BACKEND) && uv run mypy .

backend-test: ## Run backend tests (needs `make db`)
	cd $(BACKEND) && uv run pytest

backend-dev: ## Run Django dev server
	cd $(BACKEND) && uv run python manage.py runserver

frontend-install: ## Install frontend deps
	cd $(FRONTEND) && npm ci

frontend-lint: ## Lint + format-check frontend
	cd $(FRONTEND) && npm run lint:check && npm run format:check

frontend-typecheck: ## Type-check frontend
	cd $(FRONTEND) && npm run type-check

frontend-test: ## Run frontend unit tests
	cd $(FRONTEND) && npm run test:ci

frontend-build: ## Build frontend bundle
	cd $(FRONTEND) && npm run build

frontend-dev: ## Run Vite dev server
	cd $(FRONTEND) && npm run dev
