from fastapi import FastAPI

from app.api.routes.router import router


def _get_application() -> FastAPI:
    """Application Factory"""
    app = FastAPI()
    app.include_router(router=router)
    return app


app = _get_application()
