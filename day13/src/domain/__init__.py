# src/domain/__init__.py

from src.domain.models import (
    Hotel,
    Room,
    Booking,
    BookingStatus,
    AuditLog,
    AuditAction
)
from src.domain.exceptions import (
    DomainError,
    HotelNotFoundError,
    RoomNotFoundError,
    RoomNotAvailableError,
    BookingNotFoundError,
    BookingConflictError,
    InvalidDatesError,
    AuditLogNotFoundError
)

__all__ = [
    'Hotel',
    'Room',
    'Booking',
    'BookingStatus',
    'AuditLog',
    'AuditAction',
    'DomainError',
    'HotelNotFoundError',
    'RoomNotFoundError',
    'RoomNotAvailableError',
    'BookingNotFoundError',
    'BookingConflictError',
    'InvalidDatesError',
    'AuditLogNotFoundError',
]