.PHONY: help setup install run test lint format clean docker-up docker-down

help:
	@echo "NagarSeva Backend - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup:"
	@echo "  make setup              Create virtual environment and install deps"
	@echo "  make install            Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run                Run FastAPI server (development)"
	@echo "  make celery-worker      Run Celery worker"
	@echo "  make celery-beat        Run Celery beat scheduler"
	@echo "  make logs               Show server logs"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test               Run pytest"
	@echo "  make test-cov           Run tests with coverage"
	@echo "  make lint               Run ruff linter"
	@echo "  make format             Format code with black"
	@echo "  make type-check         Run mypy type checking"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up          Start all services (MongoDB, Redis, Backend)"
	@echo "  make docker-down        Stop all services"
	@echo "  make docker-build       Build Docker image"
	@echo "  make docker-logs        Show Docker logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean              Remove __pycache__ and .pyc files"
	@echo "  make clean-uploads      Remove uploaded files"
	@echo "  make reset              Full clean + remove venv"
	@echo ""

setup:
	bash setup.sh

install:
	pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

celery-worker:
	celery -A app.tasks.celery_tasks worker --loglevel=info

celery-beat:
	celery -A app.tasks.celery_tasks beat --loglevel=info

logs:
	tail -f logs/*.log

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=app --cov-report=html --cov-report=term

lint:
	ruff check app/

format:
	black app/ --line-length=100

type-check:
	mypy app/

docker-up:
	docker-compose up -d
	@echo "✅ Services started"
	@echo "   Backend: http://localhost:8000"
	@echo "   MongoDB UI: http://localhost:8081"
	@echo "   API Docs: http://localhost:8000/docs"

docker-down:
	docker-compose down
	@echo "✅ Services stopped"

docker-build:
	docker build -t nagarseva-backend:latest .

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/
	@echo "✅ Cleaned up cache files"

clean-uploads:
	rm -rf uploads/*
	@echo "✅ Cleaned up uploads"

reset: clean
	rm -rf venv/
	@echo "✅ Removed virtual environment"
	@echo "Run 'make setup' to start fresh"

.DEFAULT_GOAL := help
