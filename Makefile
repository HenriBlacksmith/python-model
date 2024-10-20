fmt:
	@black .
	@ruff check .

build:
	@docker build .
