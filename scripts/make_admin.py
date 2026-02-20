"""
One-time helper to promote a user to ADMIN locally.

Usage:
    python scripts/make_admin.py leon@test.com
"""

import sys
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User


def main(email: str):
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        if not user:
            print(f"User not found: {email}")
            return

        user.role = "ADMIN"
        db.commit()
        print(f"Updated {email} -> ADMIN")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/make_admin.py <email>")
        raise SystemExit(1)
    main(sys.argv[1])