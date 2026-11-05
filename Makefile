UV := uv run

fmt:
	@$(UV) black .
	@$(UV) ruff check --fix .

lint:
	@$(UV) black --check --diff .
	@$(UV) ruff check .
	@$(UV) ty check .

build:
	@docker build .
