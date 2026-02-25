"""
Bookings API.

- STUDENT: can create a booking request (PENDING)
- STAFF/ADMIN: can approve or reject PENDING bookings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_auth import get_current_user, require_roles
from app.core.enums import BookingStatus, UserRole
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from app.services.booking_service import (
    BookingConflictError,
    InvalidBookingTimeError,
    approve_booking,
    create_pending_booking,
    reject_booking,
)
from app.services.booking_service import cancel_booking

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a PENDING booking request.

    Anyone authenticated can request a booking, but the slot cannot already
    be occupied by an APPROVED booking.
    """
    try:
        booking = create_pending_booking(
            db,
            user_id=current_user.id,
            room_id=payload.room_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )
        return booking

    except InvalidBookingTimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except BookingConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))

    except ValueError as e:
        # e.g. room not found
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=list[BookingOut])
def list_my_bookings(
    status: BookingStatus | None = None,
    room_id: int | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List bookings for the current user with filtering + pagination.
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")

    query = select(Booking).where(Booking.user_id == current_user.id)

    if status:
        query = query.where(Booking.status == status.value)

    if room_id:
        query = query.where(Booking.room_id == room_id)

    query = query.order_by(Booking.created_at.desc()).limit(limit).offset(offset)

    rows = db.scalars(query).all()
    return list(rows)


@router.post("/{booking_id}/approve", response_model=BookingOut)
def approve(
    booking_id: int,
    db: Session = Depends(get_db),
    _staff=Depends(require_roles(UserRole.STAFF.value, UserRole.ADMIN.value)),
):
    """
    Approve a PENDING booking (STAFF/ADMIN only).

    Approval performs a final overlap check against existing APPROVED bookings.
    """
    try:
        return approve_booking(db, booking_id=booking_id)
    except BookingConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        # booking not found OR wrong status
        msg = str(e)
        raise HTTPException(status_code=404 if "not found" in msg.lower() else 400, detail=msg)


@router.post("/{booking_id}/reject", response_model=BookingOut)
def reject(
    booking_id: int,
    db: Session = Depends(get_db),
    _staff=Depends(require_roles(UserRole.STAFF.value, UserRole.ADMIN.value)),
):
    """
    Reject a PENDING booking (STAFF/ADMIN only).
    """
    try:
        return reject_booking(db, booking_id=booking_id)
    except ValueError as e:
        msg = str(e)
        raise HTTPException(status_code=404 if "not found" in msg.lower() else 400, detail=msg)
    
@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel a booking.

    - Users can cancel their own bookings
    - STAFF/ADMIN can cancel any booking
    """
    booking = db.scalar(select(Booking).where(Booking.id == booking_id))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    is_admin_or_staff = current_user.role in ["ADMIN", "STAFF"]
    if booking.user_id != current_user.id and not is_admin_or_staff:
        raise HTTPException(status_code=403, detail="Not allowed to cancel this booking")

    try:
        return cancel_booking(db, booking_id=booking_id)
    except ValueError as e:
        msg = str(e)
        raise HTTPException(
            status_code=400 if ("already" in msg.lower() or "cannot" in msg.lower()) else 404,
            detail=msg,
        )