"""
Central enums used across models, schemas, and authorization.

Keeping enums in one place avoids string drift across the codebase.
"""

from enum import Enum


class UserRole(str, Enum):
    STUDENT = "STUDENT"
    STAFF = "STAFF"
    ADMIN = "ADMIN"


class BookingStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"