"""
Booking model.

A booking links a user to a room for a time range, with a workflow status.
Double-booking prevention will be enforced at the service layer using overlap detection.
"""

from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import BookingStatus
from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Time range (stored as UTC-ish naive or timezone-aware depending on DB)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # Workflow status (default = PENDING)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=BookingStatus.PENDING.value, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships (optional but useful)
    room = relationship("Room")
    user = relationship("User")