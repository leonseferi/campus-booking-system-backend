"""
Pydantic schemas for Room endpoints.

Separates external API contracts from internal ORM models.
"""

from pydantic import BaseModel, Field

from datetime import date, datetime
from typing import List

class RoomCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50, examples=["A101"])
    name: str = Field(min_length=1, max_length=120, examples=["Study Room A101"])
    location: str | None = Field(default=None, max_length=120, examples=["Main Building - Floor 1"])
    capacity: int = Field(ge=1, le=500, default=1)


class RoomOut(BaseModel):
    id: int
    code: str
    name: str
    location: str | None
    capacity: int

    class Config:
        from_attributes = True




class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime


class RoomAvailability(BaseModel):
    room_id: int
    date: date
    booked_slots: List[TimeSlot]