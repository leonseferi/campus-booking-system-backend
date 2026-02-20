"""
Booking service.

Contains the core business logic:
- Time validation
- Overlap detection (prevents double booking)
- Approval workflow checks

Keeping this logic out of the router makes it easier to test and maintain.
"""

from datetime import datetime
from sqlalchemy import and_, or_, select, text
from sqlalchemy.orm import Session

from app.core.enums import BookingStatus
from app.models.booking import Booking
from app.models.room import Room


class BookingConflictError(Exception):
    """Raised when a booking overlaps with an existing approved booking."""
    pass


class InvalidBookingTimeError(Exception):
    """Raised when start/end times are invalid."""
    pass


def _validate_time_range(start_time: datetime, end_time: datetime) -> None:
    # Strict validation: must be increasing and non-zero duration
    if start_time >= end_time:
        raise InvalidBookingTimeError("start_time must be before end_time")


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    # Overlap exists if ranges intersect: a_start < b_end AND a_end > b_start
    return a_start < b_end and a_end > b_start


def assert_no_approved_overlap(
    db: Session,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: int | None = None,
) -> None:
    """
    Enforce: No overlaps against APPROVED bookings.

    We allow multiple PENDING requests for the same room/time (queue/approval model),
    but approval must be blocked if it would conflict with an already APPROVED booking.
    """
    _validate_time_range(start_time, end_time)

    q = select(Booking).where(
        Booking.room_id == room_id,
        Booking.status == BookingStatus.APPROVED.value,
        # overlap condition:
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    )
    if exclude_booking_id is not None:
        q = q.where(Booking.id != exclude_booking_id)

    conflict = db.scalar(q)
    if conflict:
        raise BookingConflictError("Booking conflicts with an existing approved booking")


def create_pending_booking(
    db: Session,
    *,
    user_id: int,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
) -> Booking:
    """
    Create a PENDING booking request.

    We validate:
    - room exists
    - time range is valid
    - (optional strictness) no overlap vs APPROVED bookings

    Note: For concurrency safety in SQLite, we acquire an IMMEDIATE transaction lock
    during conflict check + insert. In PostgreSQL, you'd typically use SELECT ... FOR UPDATE
    or SERIALIZABLE isolation for stronger guarantees.
    """
    _validate_time_range(start_time, end_time)

    room = db.scalar(select(Room).where(Room.id == room_id))
    if not room:
        raise ValueError("Room not found")

    # Lock DB for the shortest time possible (SQLite-friendly)
    db.execute(text("BEGIN IMMEDIATE"))

    # Prevent "requesting a slot that is already approved"
    assert_no_approved_overlap(db, room_id, start_time, end_time)

    booking = Booking(
        room_id=room_id,
        user_id=user_id,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.PENDING.value,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def approve_booking(db: Session, *, booking_id: int) -> Booking:
    """
    Approve a booking.

    Approval must fail if it conflicts with an existing APPROVED booking.
    """
    booking = db.scalar(select(Booking).where(Booking.id == booking_id))
    if not booking:
        raise ValueError("Booking not found")

    if booking.status != BookingStatus.PENDING.value:
        raise ValueError("Only PENDING bookings can be approved")

    # Lock + re-check conflicts at approval time (prevents race conditions)
    db.execute(text("BEGIN IMMEDIATE"))
    assert_no_approved_overlap(
        db,
        room_id=booking.room_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
        exclude_booking_id=booking.id,
    )

    booking.status = BookingStatus.APPROVED.value
    db.commit()
    db.refresh(booking)
    return booking


def reject_booking(db: Session, *, booking_id: int) -> Booking:
    booking = db.scalar(select(Booking).where(Booking.id == booking_id))
    if not booking:
        raise ValueError("Booking not found")

    if booking.status != BookingStatus.PENDING.value:
        raise ValueError("Only PENDING bookings can be rejected")

    booking.status = BookingStatus.REJECTED.value
    db.commit()
    db.refresh(booking)
    return booking