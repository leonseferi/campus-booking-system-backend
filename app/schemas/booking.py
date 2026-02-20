"""
Pydantic schemas for Booking endpoints.

We keep request/response models separate from ORM models to avoid leaking
internal DB structure into the external API contract.
"""

from datetime import datetime
from pydantic import BaseModel, Field

from app.core.enums import BookingStatus


class BookingCreate(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime

    # Optional note for the approver (kept simple for now)
    note: str | None = Field(default=None, max_length=300)


class BookingOut(BaseModel):
    id: int
    room_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class BookingDecision(BaseModel):
    note: str | None = Field(default=None, max_length=300)