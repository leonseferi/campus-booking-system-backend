"""
Rooms API.

Rooms represent bookable resources. Creation is restricted to STAFF/ADMIN.
Read endpoints are public (can be changed to authenticated later).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

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
def list_rooms(db: Session = Depends(get_db)):
    """
    List all rooms.
    Public by default (common pattern for browsing availability).
    """
    rooms = db.scalars(select(Room).order_by(Room.code)).all()
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