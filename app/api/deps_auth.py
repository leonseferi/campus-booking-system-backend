"""
Authentication and authorization dependencies.

This module contains reusable FastAPI dependencies for:
- Extracting JWT bearer tokens
- Decoding and validating tokens
- Loading the current authenticated user
- Enforcing role-based access control (RBAC)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.core.config import settings
from app.models.user import User


# OAuth2 scheme for extracting Bearer tokens from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate JWT token and return the associated user.

    Raises:
        401 if token is invalid or user no longer exists.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.scalar(select(User).where(User.id == int(user_id)))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_roles(*roles: str):
    """
    Role-based access guard.

    Usage:
        @router.get("/admin-only")
        def route(current_user=Depends(require_roles("ADMIN"))):
            ...
    """

    def role_dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_dependency