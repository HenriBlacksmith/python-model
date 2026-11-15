# python-model

Model project for Python

## TODO

- Change database session to use: 
https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#using-context-managers-in-dependencies-with-yield
- Add a global exception handler/middleware
- Define Core and Adapter exceptions
- Add details for the 409 code
- Add support for JWT authentication
- Add Ory OAuth authorization server to the compose setup
- Run the test database as a pytest fixture in docker
- Study logging patterns
- Add sorting and filtering to GET /users endpoint
- Investigate correlation id patterns
- Add documentation for the code with mkdocstrings
- Study performance benchmark patterns
- Study adding an adapter for an HTTP API
- Add user events using PostgreSQL LISTEN/NOTIFY and JSONL Streaming
- Add request validation tests with hypothesis
- Enforce hexagonal architecture with strict import patterns using Ruff ICN rules

## Done

- Add a paginated GET /users endpoint
- Add an asynchronous database health check
- Cleaned default FastAPI 422 codes from the OpenAPI docs
- Handle FastAPI HTTPException as RFC 9457 problem details
- Add error reponses as additional reponses in path operation details
- Improve validation error reponses using JSON pointer: https://www.rfc-editor.org/info/rfc9457/#name-the-problem-details-json-ob
