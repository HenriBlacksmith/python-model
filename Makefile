UV := uv run

all: fmt lint test build

fmt:
	@$(UV) ruff format .
	@$(UV) ruff check --fix .

lint:
	@$(UV) ruff format --check --diff .
	@$(UV) ruff check .
	@$(UV) ty check .

test:
	@$(UV) pytest .

build:
	@docker build .

run:
	@$(UV) fastapi run
