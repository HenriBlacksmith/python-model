from fastapi import FastAPI
from app.api.routes.router import router


def _get_application() -> FastAPI:
    app = FastAPI()
    app.include_router(router=router)


app = _get_application()
