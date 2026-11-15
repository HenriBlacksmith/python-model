from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
lazy from fastapi import HTTPException, Request, Response
lazy from fastapi.exceptions import RequestValidationError

from app.api.models.errors import (
    APIErrorResponse,
    APIValidationError,
    APIValidationErrorResponse,
    ProblemJSONResponse,
)


async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    return ProblemJSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            APIErrorResponse(
                title=exc.detail,
                status=exc.status_code,
                instance=request.url.path,
            ),
            exclude_none=True,
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    return ProblemJSONResponse(
        status_code=500,
        content=jsonable_encoder(
            APIErrorResponse(
                title="An unexpected error occurred.",
                status=500,
                instance=request.url.path,
            ),
            exclude_none=True,
        ),
    )


def _loc_to_json_pointer(loc: str) -> str:
    return "#/" + "/".join(loc[1:])


async def validation_exception_handler(
    request: Request, err: RequestValidationError
) -> Response:
    return JSONResponse(
        status_code=400,
        media_type="application/problem+json",
        content=jsonable_encoder(
            APIValidationErrorResponse(
                detail=None,
                instance=request.url.path,
                errors=[
                    APIValidationError(
                        pointer=str(_loc_to_json_pointer(e["loc"])),
                        detail=str(e["msg"]),
                    )
                    for e in err.errors()
                ],
            ),
            exclude_none=True,
        ),
    )
