from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
lazy from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes

from app.adapters.configuration.settings import settings

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{settings.auth.issuer}oauth2/auth",
    tokenUrl=f"{settings.auth.issuer}oauth2/token",
    auto_error=False,
)

jwks_client = jwt.PyJWKClient(settings.auth.jwks_url.unicode_string())


def _get_token(token: Annotated[str | None, Depends(oauth2_scheme)]) -> str:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(_get_token)],
) -> dict[str, Any]:
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            key=signing_key.key,
            algorithms=["RS256"],
            issuer=str(settings.auth.issuer),
            audience=settings.auth.audience,
        )
    except (jwt.InvalidTokenError, jwt.PyJWKClientError) as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
    _check_scopes(claims, security_scopes)
    return claims


def _granted_scopes(claims: dict[str, Any]) -> set[str]:
    granted = claims.get(settings.auth.scope_claim) or []
    if isinstance(granted, str):
        return set(granted.split())
    return set(granted)


def _check_scopes(claims: dict[str, Any], security_scopes: SecurityScopes) -> None:
    if set(security_scopes.scopes).issubset(_granted_scopes(claims)):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient scopes.",
        headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'},
    )


CurrentUser = Annotated[dict[str, Any], Depends(get_current_user)]
