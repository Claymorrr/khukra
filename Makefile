.PHONY: setup setup-seed dev test smoke typecheck help

help:
	@echo "Khukra Logistics"
	@echo "  make setup       - venv + pip + npm install"
	@echo "  make setup-seed  - setup + ingest 5y demo data"
	@echo "  make dev         - start API + UI (use scripts on Windows)"
	@echo "  make test        - pytest"
	@echo "  make smoke       - pytest + API health if running"
	@echo "  make typecheck   - frontend TypeScript check"

setup:
	python3 -m venv .venv || python -m venv .venv
	.venv/bin/pip install -e ".[dev]" || .venv/Scripts/pip install -e ".[dev]"
	cd frontend && npm install

setup-seed: setup
	.venv/bin/khukra-logistics refresh --years 5 || .venv/Scripts/khukra-logistics.exe refresh --years 5
	.venv/bin/khukra-logistics refresh-news || .venv/Scripts/khukra-logistics.exe refresh-news

test:
	.venv/bin/python -m pytest tests/ -q || .venv/Scripts/python.exe -m pytest tests/ -q

smoke:
	./scripts/smoke-test.sh || powershell -File scripts/smoke-test.ps1

typecheck:
	cd frontend && npm run typecheck

dev:
	@echo "Windows: .\\scripts\\start-dev.ps1"
	@echo "Mac/Linux: ./scripts/start-dev.sh"
