class DomainError(Exception):
    """Базовое исключение домена"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

class HotelNotFoundError(DomainError):
    pass

class RoomNotFoundError(DomainError):
    pass

class RoomNotAvailableError(DomainError):
    pass

class BookingNotFoundError(DomainError):
    pass

class BookingConflictError(DomainError):
    """Пересечение бронирований на один номер"""
    pass

class InvalidDatesError(DomainError):
    pass

class AuditLogNotFoundError(DomainError):
    pass