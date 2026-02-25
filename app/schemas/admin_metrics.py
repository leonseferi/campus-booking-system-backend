from pydantic import BaseModel


class AdminMetricsOut(BaseModel):
    total_rooms: int
    total_users: int
    total_bookings: int
    pending_bookings: int
    approved_bookings: int
    rejected_bookings: int
    cancelled_bookings: int