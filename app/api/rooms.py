"""
Rooms API.

Rooms represent bookable resources. Creation is restricted to STAFF/ADMIN.
Read endpoints are public (can be changed to authenticated later).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date, datetime, time, timedelta
from app.schemas.room import RoomAvailability, TimeSlot
from app.core.enums import BookingStatus
from app.models.booking import Booking
from app.api.deps import get_db
from app.api.deps_auth import require_roles
from app.core.enums import UserRole
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomOut

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post(
    "",
    response_model=RoomOut,
    status_code=status.HTTP_201_CREATED,
)
def create_room(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_roles(UserRole.STAFF.value, UserRole.ADMIN.value)),
):
    """
    Create a new room.

    Restricted to STAFF/ADMIN to prevent untrusted users from creating resources.
    """
    existing = db.scalar(select(Room).where(Room.code == payload.code))
    if existing:
        raise HTTPException(status_code=409, detail="Room code already exists")

    room = Room(
        code=payload.code.strip(),
        name=payload.name.strip(),
        location=payload.location.strip() if payload.location else None,
        capacity=payload.capacity,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("", response_model=list[RoomOut])
def list_rooms(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List rooms with pagination.

    Default: limit=20, offset=0
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")

    rooms = db.scalars(
        select(Room)
        .order_by(Room.code)
        .limit(limit)
        .offset(offset)
    ).all()

    return list(rooms)


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single room by id.
    """
    room = db.scalar(select(Room).where(Room.id == room_id))
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.get("/{room_id}/availability", response_model=RoomAvailability)
def get_room_availability(
    room_id: int,
    date: date,
    db: Session = Depends(get_db),
):
    """
    Return all APPROVED bookings for a room on a specific date.
    """

    room = db.scalar(select(Room).where(Room.id == room_id))
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    start_of_day = datetime.combine(date, time.min)
    end_of_day = datetime.combine(date, time.max)

    bookings = db.scalars(
        select(Booking).where(
            Booking.room_id == room_id,
            Booking.status == BookingStatus.APPROVED.value,
            Booking.start_time < end_of_day,
            Booking.end_time > start_of_day,
        )
    ).all()

    slots = [
        TimeSlot(
            start_time=b.start_time,
            end_time=b.end_time,
        )
        for b in bookings
    ]

    return RoomAvailability(
        room_id=room_id,
        date=date,
        booked_slots=slots,
    )