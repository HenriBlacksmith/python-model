# python-model

Model project for Python

## TODO

- Change database session to use: 
https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#using-context-managers-in-dependencies-with-yield
- Add a global exception handler/middleware
- Define Core and Adapter exceptions
- Handle FastAPI HTTPException as RFC 9457 problem details
- Improve validation error reponses
- Cleanup 422 code from the API docs
- Add error reponses as additional reponses in path operation details
- Add support for JWT authentication
- Add Ory OAuth authorization server to the compose setup
- Run the test database as a pytest fixture in docker
- Study logging patterns
- Investigate correlation id patterns
- Add an asynchronous database health check

