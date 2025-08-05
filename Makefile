.PHONY: install install-dev test lint format clean run-api run-web

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

# Testing
test:
	pytest

test-cov:
	pytest --cov=src --cov-report=html

# Code quality
lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

# Running
run-api:
	python -m src.api.main

run-web:
	streamlit run src/web/dashboard.py

run-main:
	python -m src.main

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

# Database
db-init:
	python src/database/init_db.py

db-setup:
	python scripts/setup_database.py

db-test:
	pytest tests/test_database.py -v

# Development setup
setup-dev: install-dev
	cp .env.example .env
	@echo "Development environment setup complete!"
	@echo "Edit .env file with your configuration"
	@echo "Run 'make db-setup' to initialize the database"