.SILENT:

# =============================================================================
# SKIM KERNEL - Makefile with UV
# =============================================================================
# UV-powered Python project management
# =============================================================================

.PHONY: help
help: ## Show this help message
	echo "skim-kernel - News Aggregation & Summarization Platform"
	echo ""
	echo "Available commands:"
	echo ""
	awk 'BEGIN {FS=":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	echo ""
	echo "Examples:"
	echo "  make install          # Install all dependencies"
	echo "  make run-summ         # Run summarization service"
	echo "  make test             # Run tests"
	echo ""

# =============================================================================
# UV & DEPENDENCY MANAGEMENT
# =============================================================================

.PHONY: install
install: ## Install dependencies with UV
	uv sync

.PHONY: install-dev
install-dev: ## Install with dev dependencies
	uv sync --group dev

.PHONY: install-no-dev
install-no-dev: ## Install without dev dependencies (production only)
	uv sync --no-dev-groups

.PHONY: update
update: ## Update all dependencies
	uv sync --upgrade

.PHONY: lock
lock: ## Update uv.lock file
	uv lock --upgrade

.PHONY: clean
clean: ## Remove .venv and cache directories
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache .coverage
	uv cache clean

.PHONY: create_venv
create_venv: ## Create Python virtual environment using UV
	uv venv

.PHONY: gen-req
gen-req: ## Generate requirements.txt from UV environment (for backward compatibility)
	uv pip freeze | grep -v "^-e " > requirements.txt

# =============================================================================
# CODE QUALITY
# =============================================================================

.PHONY: fmt
fmt: ## Format code with black and ruff
	uv run ruff format .
	uv run ruff check --fix .

.PHONY: lint
lint: ## Run linters (ruff)
	uv run ruff check .

.PHONY: typecheck
typecheck: ## Run type checker (mypy)
	uv run mypy .

.PHONY: check
check: lint typecheck ## Run all checks (lint + typecheck)

# =============================================================================
# TESTING
# =============================================================================

.PHONY: test
test: ## Run all tests
	uv run pytest

.PHONY: test-cov
test-cov: ## Run tests with coverage
	uv run pytest --cov=. --cov-report=html --cov-report=term

.PHONY: test-v
test-v: ## Run tests with verbose output
	uv run pytest -v

.PHONY: test-unit
test-unit: ## Run unit tests only
	uv run pytest tests/unit

.PHONY: test-integration
test-integration: ## Run integration tests only
	uv run pytest tests/integration

# =============================================================================
# DATABASE (Alembic)
# =============================================================================

.PHONY: gen-db
gen-db: ## Generate Alembic migration (usage: make gen-db NAME="add users table")
	uv run alembic revision --autogenerate -m "$(NAME)"

.PHONY: apply-db
apply-db: ## Apply latest database migrations
	uv run alembic upgrade head

.PHONY: downgrade-db
downgrade-db: ## Downgrade database by one version
	uv run alembic downgrade -1

.PHONY: db-history
db-history: ## Show migration history
	uv run alembic history

.PHONY: db-current
db-current: ## Show current migration version
	uv run alembic current

# =============================================================================
# SERVICE RUNNING
# =============================================================================

.PHONY: run-rss
run-rss: ## Run RSS feed service (kalinga)
	uv run python main.py kalinga

.PHONY: run-scrap
run-scrap: ## Run scraping service (bundelkhand)
	uv run python main.py bundelkhand

.PHONY: run-summ
run-summ: ## Run summarization service (amarkantak)
	uv run python main.py amarkantak

.PHONY: run-all
run-all: ## Run all services together (mahabharat)
	uv run python main.py mahabharat

# =============================================================================
# INFRASTRUCTURE (Docker)
# =============================================================================

.PHONY: db-up
db-up: ## Start PostgreSQL database
	docker compose -f docker-compose-db.yml up -d

.PHONY: db-down
db-down: ## Stop PostgreSQL database
	docker compose -f docker-compose-db.yml down

.PHONY: mq-up
mq-up: ## Start RabbitMQ message queue
	docker compose -f docker-compose-msg-queue.yml up -d

.PHONY: mq-down
mq-down: ## Stop RabbitMQ message queue
	docker compose -f docker-compose-msg-queue.yml down

.PHONY: infra-up
infra-up: ## Start all infrastructure (DB + MQ)
	$(MAKE) db-up
	$(MAKE) mq-up

.PHONY: infra-down
infra-down: ## Stop all infrastructure
	$(MAKE) db-down
	$(MAKE) mq-down

.PHONY: infra-logs
infra-logs: ## Show infrastructure logs
	docker compose -f docker-compose-db.yml logs -f
	docker compose -f docker-compose-msg-queue.yml logs -f

# =============================================================================
# DEV WORKFLOWS
# =============================================================================

.PHONY: dev-setup
dev-setup: ## Full development setup: infra up + install + apply migrations
	$(MAKE) infra-up
	$(MAKE) install-dev
	$(MAKE) apply-db

.PHONY: dev-reset
dev-reset: ## Reset development environment
	$(MAKE) infra-down
	$(MAKE) clean
	rm -f uv.lock
	$(MAKE) dev-setup

.PHONY: quick-start
quick-start: ## Quick start for summarizer service
	$(MAKE) mq-up
	$(MAKE) install
	$(MAKE) run-summ

# =============================================================================
# DOCKER BUILD (for production/containerization)
# =============================================================================

.PHONY: docker-build
docker-build: ## Build Docker image with UV
	docker build -t skim-kernel:latest .

.PHONY: docker-run
docker-run: ## Run Docker container
	docker run -it --rm skim-kernel:latest
