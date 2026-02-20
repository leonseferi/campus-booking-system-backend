"""
Room model.

Represents a bookable campus space (e.g., lecture room, study room, lab).
"""

from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Human-friendly identifier (e.g., "A101", "Library-2F-12")
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # Optional descriptive fields
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    location: Mapped[str] = mapped_column(String(120), nullable=True)

    # Basic constraint used later for booking validation/rules
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)