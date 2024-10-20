FROM python:3.13.0-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.4.24 /uv /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["uvicorn", "main:app", "--port", "8000", "--host", "0.0.0.0"]
