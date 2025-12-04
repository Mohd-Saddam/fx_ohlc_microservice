.PHONY: help install install-dev setup test test-cov lint format clean docker-build docker-run docker-stop

# Help command
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  setup        - Setup development environment"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code"
	@echo "  clean        - Clean temporary files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker Compose"
	@echo "  init-db      - Initialize database"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements-dev.txt

# Setup development environment
setup: install-dev
	pre-commit install
	@echo "Development environment setup complete!"

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

# Run linting
lint:
	flake8 app tests
	mypy app
	black --check app tests
	isort --check-only app tests

# Format code
format:
	black app tests
	isort app tests

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# Docker commands
docker-build:
	docker build -t fx-ohlc-microservice .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database initialization
init-db:
	python scripts/init_db.py

# Run development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run production server
prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Generate requirements
freeze:
	pip freeze > requirements.txt

# Database migration (placeholder for Alembic)
migrate:
	@echo "Migrations not yet implemented. Use init-db for now."

# Backup database
backup-db:
	docker-compose exec db pg_dump -U postgres fx_ohlc > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Performance test
perf-test:
	@echo "Performance tests not yet implemented."

# Security scan
security:
	pip-audit
	bandit -r app/

# Start monitoring stack
monitor:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up prometheus grafana -d