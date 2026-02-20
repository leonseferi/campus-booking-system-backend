"""
Administrative user management endpoints.

Restricted to ADMIN role.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_auth import require_roles
from app.core.enums import UserRole
from app.models.user import User
from app.schemas.user import UserOut
from app.schemas.user_admin import UserRoleUpdate

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


@router.patch("/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_roles(UserRole.ADMIN.value)),
):
    """
    Update a user's role.

    ADMIN only.
    """
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Optional safety: prevent admin from demoting themselves
    if user.id == current_admin.id and payload.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own ADMIN role",
        )

    user.role = payload.role.value
    db.commit()
    db.refresh(user)

    return user