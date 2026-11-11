from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
lazy from fastapi import Request, Response
lazy from fastapi.exceptions import RequestValidationError

from app.api.models.errors import APIErrorResponse


async def validation_exception_handler(
    request: Request, _: RequestValidationError
) -> Response:
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(
            APIErrorResponse(
                title="The request was invalid.",
                status=400,
                detail="",
                instance=request.url.path,
            )
        ),
    )
