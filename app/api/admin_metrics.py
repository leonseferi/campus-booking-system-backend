from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_auth import require_roles
from app.core.enums import BookingStatus, UserRole
from app.models.booking import Booking
from app.models.room import Room
from app.models.user import User
from app.schemas.admin_metrics import AdminMetricsOut

router = APIRouter(prefix="/admin/metrics", tags=["admin-metrics"])


@router.get("", response_model=AdminMetricsOut)
def get_metrics(
    db: Session = Depends(get_db),
    _admin=Depends(require_roles(UserRole.ADMIN.value)),
):
    total_rooms = db.scalar(select(func.count(Room.id))) or 0
    total_users = db.scalar(select(func.count(User.id))) or 0
    total_bookings = db.scalar(select(func.count(Booking.id))) or 0

    def count_status(status: BookingStatus) -> int:
        return db.scalar(
            select(func.count(Booking.id)).where(Booking.status == status.value)
        ) or 0

    return AdminMetricsOut(
        total_rooms=total_rooms,
        total_users=total_users,
        total_bookings=total_bookings,
        pending_bookings=count_status(BookingStatus.PENDING),
        approved_bookings=count_status(BookingStatus.APPROVED),
        rejected_bookings=count_status(BookingStatus.REJECTED),
        cancelled_bookings=count_status(BookingStatus.CANCELLED),
    )