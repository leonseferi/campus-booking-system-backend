"""
Alembic metadata bridge.

Importing models here ensures they are registered on Base.metadata
without introducing circular imports into runtime modules.
"""

from app.db.base import Base
from app.models.user import User  # noqa: F401
from app.models.room import Room  # noqa: F401
from app.models.booking import Booking  # noqa: F401

target_metadata = Base.metadata