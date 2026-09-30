# 로컬 검증은 외부 API를 호출하지 않는다.
.PHONY: check-language check-secrets test-harness check-design lint test migrate seed api web gen-api
UV_CACHE_DIR ?= /private/tmp/itemsourcing-uv-cache
export UV_CACHE_DIR

check-language:
	python3 harness/check_language.py

check-secrets:
	backend/.venv/bin/python harness/check_secrets.py

test-harness:
	python3 -m unittest discover -s harness/tests -v

check-design: test-harness check-language

lint: check-language check-secrets
	cd backend && uv run ruff check app scripts tests
	cd backend && uv run ruff format --check app scripts tests
	cd backend && uv run mypy app
	cd frontend && npm run lint
	cd frontend && npm run format:check

test: test-harness
	cd backend && uv run pytest -q
	cd frontend && npm run test

migrate:
	cd backend && uv run alembic upgrade head

seed:
	cd backend && uv run python -m app.db.seed

api:
	cd backend && uv run uvicorn app.main:app --reload

web:
	cd frontend && npm run dev

gen-api:
	cd frontend && npm run gen:api
