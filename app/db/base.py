from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models so Alembic can discover them via Base.metadata
from app.models.user import User  # noqa: E402,F401
from app.models.room import Room  # noqa: E402,F401
from app.models.booking import Booking  # noqa: E402,F401