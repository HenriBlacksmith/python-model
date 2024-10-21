fmt:
	@black .
	@isort .
	@ruff check --fix .

lint:
	@black --check --diff .
	@isort --check --diff .
	@ruff check --fix .

build:
	@docker build .
