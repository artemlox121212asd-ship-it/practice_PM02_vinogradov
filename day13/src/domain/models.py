from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional

class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

class AuditAction(Enum):
    CREATE = "create"
    UPDATE = "update"
    CANCEL = "cancel"
    CONFIRM = "confirm"
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    DELETE = "delete"

@dataclass
class Hotel:
    id: Optional[int]
    name: str
    address: str
    phone: str
    rating: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Room:
    id: Optional[int]
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    is_active: bool = True
    room_type: str = "standard"

@dataclass
class Booking:
    id: Optional[int]
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    total_price: float
    status: BookingStatus = BookingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    cancelled_at: Optional[datetime] = None

@dataclass
class AuditLog:
    id: Optional[int]
    booking_id: int
    action: AuditAction
    user_id: Optional[int]
    user_role: str
    old_values: dict
    new_values: dict
    timestamp: datetime = field(default_factory=datetime.now)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None