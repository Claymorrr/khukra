from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from khukra.auth.security import decode_token
from khukra.data.repositories.users import UserRepository

security = HTTPBearer(auto_error=False)
users = UserRepository()

ROLE_HIERARCHY = {"viewer": 0, "analyst": 1, "admin": 2}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict | None:
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if not payload:
        return None
    return users.get_by_id(payload["sub"])


async def require_user(user: dict | None = Depends(get_current_user)) -> dict:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def _role_level(role: str) -> int:
    return ROLE_HIERARCHY.get(role or "viewer", 0)


def require_roles(*allowed: str):
    """Dependency factory: user must have one of the allowed roles (admin always passes)."""

    async def _checker(user: dict = Depends(require_user)) -> dict:
        role = user.get("role") or "viewer"
        if role == "admin" or role in allowed:
            return user
        if _role_level(role) >= max(_role_level(r) for r in allowed):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{role}' not permitted for this action",
        )

    return _checker


require_analyst = require_roles("analyst", "admin")
require_admin = require_roles("admin")
