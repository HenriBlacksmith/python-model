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
	@FASTAPI_OTEL_AUTO_CONFIGURE=true \
		OTEL_SERVICE_NAME=my-api \
		OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318 \
		$(UV) fastapi run

run-monitoring:
	@docker compose --file monitoring/compose.yml up --detach
