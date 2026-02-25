"""
Booking service.

Contains the core business logic:
- Time validation
- Overlap detection (prevents double booking)
- Approval workflow checks

Keeping this logic out of the router makes it easier to test and maintain.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.enums import BookingStatus
from app.models.booking import Booking
from app.models.room import Room


class BookingConflictError(Exception):
    """Raised when a booking overlaps with an existing booking."""


class InvalidBookingTimeError(Exception):
    """Raised when start/end times are invalid."""


def _validate_time_range(start_time: datetime, end_time: datetime) -> None:
    # Strict validation: must be increasing and non-zero duration
    if start_time >= end_time:
        raise InvalidBookingTimeError("start_time must be before end_time")


def _validate_booking_window(start_time: datetime, end_time: datetime) -> None:
    """
    Extra business rules:
    - booking must be in the future
    - minimum duration (15 minutes)
    - maximum duration (4 hours)
    """
    _validate_time_range(start_time, end_time)

    duration = end_time - start_time
    if duration < timedelta(minutes=15):
        raise InvalidBookingTimeError("Booking duration must be at least 15 minutes")

    if duration > timedelta(hours=4):
        raise InvalidBookingTimeError("Booking duration cannot exceed 4 hours")

    # Compare using UTC if datetime is timezone-aware
    now = datetime.now(timezone.utc) if start_time.tzinfo else datetime.now()
    if start_time < now:
        raise InvalidBookingTimeError("Bookings must start in the future")


def assert_no_approved_overlap(
    db: Session,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: int | None = None,
) -> None:
    """
    Enforce: No overlaps against APPROVED bookings.

    Approval must be blocked if it would conflict with an already APPROVED booking.
    """
    _validate_booking_window(start_time, end_time)

    q = select(Booking).where(
        Booking.room_id == room_id,
        Booking.status == BookingStatus.APPROVED.value,
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    )

    if exclude_booking_id is not None:
        q = q.where(Booking.id != exclude_booking_id)

    conflict = db.scalar(q)
    if conflict:
        raise BookingConflictError("Booking conflicts with an existing approved booking")


def assert_no_active_overlap(
    db: Session,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: int | None = None,
) -> None:
    """
    Enforce: No overlaps against ACTIVE bookings (PENDING or APPROVED).

    This prevents duplicate/competing requests for the same room/time window.
    """
    _validate_booking_window(start_time, end_time)

    q = select(Booking).where(
        Booking.room_id == room_id,
        Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.APPROVED.value]),
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    )

    if exclude_booking_id is not None:
        q = q.where(Booking.id != exclude_booking_id)

    conflict = db.scalar(q)
    if conflict:
        raise BookingConflictError("Room already booked for this time range")


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
    - booking window is valid
    - no overlap vs ACTIVE bookings (PENDING or APPROVED)

    SQLite note: BEGIN IMMEDIATE is used to reduce race conditions during
    conflict check + insert.
    """
    _validate_booking_window(start_time, end_time)

    room = db.scalar(select(Room).where(Room.id == room_id))
    if not room:
        raise ValueError("Room not found")

    db.execute(text("BEGIN IMMEDIATE"))
    assert_no_active_overlap(db, room_id, start_time, end_time)

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


def cancel_booking(db: Session, *, booking_id: int) -> Booking:
    booking = db.scalar(select(Booking).where(Booking.id == booking_id))
    if not booking:
        raise ValueError("Booking not found")

    if booking.status == BookingStatus.CANCELLED.value:
        raise ValueError("Booking already cancelled")

    if booking.status == BookingStatus.REJECTED.value:
        raise ValueError("Rejected bookings cannot be cancelled")

    booking.status = BookingStatus.CANCELLED.value
    db.commit()
    db.refresh(booking)
    return booking