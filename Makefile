package_dir := src
test_dir := tests
code_dir := $(package_dir)

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install dependencies
	pip3 install -r requirements.txt

.PHONY: run_local
run_local: ## Run the application locally
	python3 -m $(package_dir)

.PHONY: run_test_local
run_test_local: ## Run tests locally
	pytest ${test_dir}

.PHONY: docker_build
docker_build: ## Build Docker image
	docker-compose build

.PHONY: docker_rebuild
docker_rebuild: ## Rebuild Docker image
	docker-compose down
	docker-compose build --no-cache

.PHONY: docker_up
docker_up: ## Run Docker container
	docker-compose up -d

.PHONY: docker_down
docker_down: ## Stop Docker container
	docker-compose down

.PHONY: alembic_upgrade
alembic_upgrade: ## Run Alembic migrations
	alembic upgrade head

.PHONY: alembic_downgrade
alembic_downgrade: ## Rollback Alembic migrations
	alembic downgrade -1