# Day-to-day commands. On PowerShell use ./infra/dev.ps1 <target> instead.
COMPOSE := docker compose -f infra/docker-compose.yml

.PHONY: up down test lint migrate revision

.env:
	cp .env.example .env

up: .env
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

test:
	cd backend && uv run pytest

lint:
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run lint-imports

migrate:
	$(COMPOSE) run --rm api alembic upgrade head

revision:
	@test -n "$(m)" || (echo 'usage: make revision m="describe the change"' && exit 1)
	$(COMPOSE) run --rm api alembic revision --autogenerate -m "$(m)"
