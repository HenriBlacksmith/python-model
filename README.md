# python-model

Model project for Python

## Getting started

### Prerequisites

- Python 3.15+ managed with [uv](https://docs.astral.sh/uv/)
- Docker

### Run the API

```bash
make run
```

This starts PostgreSQL and Ory Hydra with Docker, applies database migrations
and serves the API on <http://127.0.0.1:8000>. The OpenAPI docs are available
at <http://127.0.0.1:8000/docs>.

### Authentication

Protected endpoints validate JWT access tokens issued by the local
[Ory Hydra](https://www.ory.com/docs/hydra) instance (<http://127.0.0.1:4444>),
using its JWKS endpoint. Required scopes:

- `users:read` for the `GET /users` endpoints
- `users:write` for the `POST`, `PUT` and `DELETE /users` endpoints

The `/health` and `/user_events` endpoints are public.

The scope claim name read from access tokens is configurable with
`auth.scope_claim` in `config.yaml` (default `scp`, as used by Hydra).

## Development

- `make lint`: ruff format/check and ty
- `make test`: pytest against PostgreSQL and Hydra started with Docker
- `make all`: format, lint, test and Docker build

## TODO

- Change database session to use: 
https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#using-context-managers-in-dependencies-with-yield
- Add adapter-level exceptions mapped to problem+json responses
- Run the test database as a pytest fixture in docker
- Study logging patterns, propagate the correlation id and the token subject
- Add sorting and filtering to GET /users endpoint
- Investigate correlation id patterns
- Add documentation for the code with mkdocstrings
- Study performance benchmark patterns
- Study adding an adapter for an HTTP API
- Add request validation tests with hypothesis
- Enforce hexagonal architecture with strict import patterns using Ruff ICN rules
- Inject the authenticated user claims (CurrentUser) into the controllers
- Bootstrap an Ory Hydra OAuth client in the compose setup
- Authenticate the SSE /user_events endpoint
- Study JWKS rotation and key cache refresh
- Add optional integration tests against a real Hydra instance
- Add a coverage gate to the test job
- Add pre-commit hooks (ruff, ty)
- Add dependency updates (Dependabot or Renovate)
- Add pip-audit to the CI
- Externalize Hydra and PostgreSQL secrets from the compose file
- Add an Alembic schema drift check to the CI
- Add rate limiting

## Done

- Validate the access token audience (auth.audience, optional)
- Add a paginated GET /users endpoint
- Add an asynchronous database health check
- Cleaned default FastAPI 422 codes from the OpenAPI docs
- Handle FastAPI HTTPException as RFC 9457 problem details
- Add error reponses as additional reponses in path operation details
- Improve validation error reponses using JSON pointer: https://www.rfc-editor.org/info/rfc9457/#name-the-problem-details-json-ob
- Handle unhandled exceptions as RFC 9457 problem details and log them
- Handle username conflicts with 409 problem+json responses on creation and update
- Add user events streaming with PostgreSQL LISTEN/NOTIFY and SSE
- Add JWT authentication with PyJWT, validated against Ory Hydra (JWKS, issuer)
- Enforce users:read and users:write scopes per route with Security and SecurityScopes
- Make the access token scope claim name configurable (auth.scope_claim)
- Document 401/403 responses in the OpenAPI specification of protected routes
- Factorize OpenAPI error responses into reusable constants
- Forward WWW-Authenticate headers in problem+json responses
- Add Ory Hydra to the compose setup (hydra and hydra-migrate services)
