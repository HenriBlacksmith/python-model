from typing import Annotated, Any
lazy from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
lazy from fastapi.security import OAuth2AuthorizationCodeBearer

from app.adapters.configuration.settings import settings

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{settings.auth.issuer}oauth2/auth",
    tokenUrl=f"{settings.auth.issuer}oauth2/token",
    auto_error=False,
)

jwks_client = jwt.PyJWKClient(settings.auth.jwks_url.unicode_string())

_UNAUTHORIZED_HEADERS = {"WWW-Authenticate": "Bearer"}


def _get_token(token: Annotated[str | None, Depends(oauth2_scheme)]) -> str:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token.",
            headers=_UNAUTHORIZED_HEADERS,
        )
    return token


def get_current_user(token: Annotated[str, Depends(_get_token)]) -> dict[str, Any]:
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            key=signing_key.key,
            algorithms=["RS256"],
            issuer=str(settings.auth.issuer),
        )
    except (jwt.InvalidTokenError, jwt.PyJWKClientError) as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers=_UNAUTHORIZED_HEADERS,
        ) from err
    return claims


CurrentUser = Annotated[dict[str, Any], Depends(get_current_user)]


def require_scopes(
    *required_scopes: str,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def _check_scopes(claims: CurrentUser) -> dict[str, Any]:
        granted = claims.get("scp") or claims.get("scope") or []
        if isinstance(granted, str):
            granted = granted.split()
        if not set(required_scopes).issubset(granted):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient scopes.",
            )
        return claims

    return _check_scopes
