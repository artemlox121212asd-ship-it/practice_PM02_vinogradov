# src/services/booking_service.py

from datetime import date, datetime
from typing import List, Optional
from src.domain.models import Booking, BookingStatus, AuditAction
from src.domain.exceptions import (
    RoomNotFoundError,
    BookingConflictError,
    BookingNotFoundError,
    DomainError
)
from src.dto.booking_dto import BookingCreateDTO, BookingResponseDTO, BookingUpdateDTO
from src.dto.audit_dto import AuditLogDTO
from src.uow.unit_of_work import UnitOfWork
from src.services.pricing_service import PricingService
from src.services.audit_service import AuditService


class BookingService:
    """Сервис для управления бронированиями с интегрированным аудитом."""

    def __init__(self, uow: UnitOfWork, pricing_service: PricingService):
        self.uow = uow
        self.pricing_service = pricing_service
        self.booking_repo = uow.bookings
        self.room_repo = uow.rooms
        self.audit_service = AuditService(uow)
        self._current_user_id = None
        self._current_user_role = 'system'

    def set_user_context(self, user_id: Optional[int], role: str = 'system'):
        """Установить контекст пользователя для аудита."""
        self._current_user_id = user_id
        self._current_user_role = role

    def create(self, dto: BookingCreateDTO) -> BookingResponseDTO:
        """Создать новое бронирование с аудитом."""
        room = self.room_repo.get_by_id(dto.room_id)
        if not room or not room.is_active:
            raise RoomNotFoundError(f"Номер {dto.room_id} не найден или не активен")

        existing = self.booking_repo.get_by_room_and_dates(
            dto.room_id, dto.check_in, dto.check_out
        )
        if existing:
            raise BookingConflictError(
                f"Номер {dto.room_id} уже забронирован на эти даты",
                details={"conflicting_bookings": [b.id for b in existing]}
            )

        total_price = self.pricing_service.calculate_price(
            room, dto.check_in, dto.check_out
        )

        booking = Booking(
            id=None,
            room_id=dto.room_id,
            guest_name=dto.guest_name,
            guest_email=dto.guest_email,
            check_in=dto.check_in,
            check_out=dto.check_out,
            total_price=total_price,
            status=BookingStatus.PENDING
        )

        saved = self.booking_repo.add(booking)
        self.uow.commit()

        self.audit_service.log_action(
            booking_id=saved.id,
            action=AuditAction.CREATE,
            user_id=self._current_user_id,
            user_role=self._current_user_role,
            old_values={},
            new_values={
                'room_id': saved.room_id,
                'guest_name': saved.guest_name,
                'guest_email': saved.guest_email,
                'check_in': saved.check_in.isoformat(),
                'check_out': saved.check_out.isoformat(),
                'total_price': saved.total_price,
                'status': saved.status.value
            }
        )

        return BookingResponseDTO.model_validate(saved)

    def cancel(self, booking_id: int) -> bool:
        """Отменить бронирование с аудитом."""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")

        if booking.status in (BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT):
            raise DomainError(
                f"Нельзя отменить бронирование в статусе {booking.status.value}"
            )

        old_state = {
            'status': booking.status.value,
            'guest_name': booking.guest_name,
            'guest_email': booking.guest_email,
            'check_in': booking.check_in.isoformat(),
            'check_out': booking.check_out.isoformat(),
            'total_price': booking.total_price
        }

        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now()
        self.booking_repo.update(booking)
        self.uow.commit()

        self.audit_service.log_action(
            booking_id=booking.id,
            action=AuditAction.CANCEL,
            user_id=self._current_user_id,
            user_role=self._current_user_role,
            old_values=old_state,
            new_values={
                'status': BookingStatus.CANCELLED.value,
                'cancelled_at': booking.cancelled_at.isoformat()
            }
        )

        return True

    def confirm(self, booking_id: int) -> None:
        """Подтвердить бронирование с аудитом."""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")

        if booking.status != BookingStatus.PENDING:
            raise DomainError(
                f"Бронирование в статусе {booking.status.value} нельзя подтвердить"
            )

        old_state = {'status': booking.status.value}
        booking.status = BookingStatus.CONFIRMED
        self.booking_repo.update(booking)
        self.uow.commit()

        self.audit_service.log_action(
            booking_id=booking.id,
            action=AuditAction.CONFIRM,
            user_id=self._current_user_id,
            user_role=self._current_user_role,
            old_values=old_state,
            new_values={'status': BookingStatus.CONFIRMED.value}
        )

    def update(self, booking_id: int, dto: BookingUpdateDTO) -> BookingResponseDTO:
        """Обновить бронирование с аудитом."""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")

        old_state = {
            'guest_name': booking.guest_name,
            'guest_email': booking.guest_email
        }

        if dto.guest_name is not None:
            booking.guest_name = dto.guest_name
        if dto.guest_email is not None:
            booking.guest_email = dto.guest_email

        self.booking_repo.update(booking)
        self.uow.commit()

        self.audit_service.log_action(
            booking_id=booking.id,
            action=AuditAction.UPDATE,
            user_id=self._current_user_id,
            user_role=self._current_user_role,
            old_values=old_state,
            new_values={
                'guest_name': booking.guest_name,
                'guest_email': booking.guest_email
            }
        )

        return BookingResponseDTO.model_validate(booking)

    def get_booking_history(self, booking_id: int) -> List[AuditLogDTO]:
        """Получить историю изменений бронирования."""
        return self.audit_service.get_booking_history(booking_id)

    def get_available_rooms(
        self,
        hotel_id: int,
        check_in: date,
        check_out: date,
        capacity: Optional[int] = None
    ) -> List[dict]:
        """Получить доступные номера в отеле на указанные даты."""
        rooms = self.room_repo.get_by_hotel(hotel_id, active_only=True)

        if capacity:
            rooms = [r for r in rooms if r.capacity >= capacity]

        available = []
        for room in rooms:
            existing = self.booking_repo.get_by_room_and_dates(
                room.id, check_in, check_out
            )
            if not existing:
                available.append({
                    'room_id': room.id,
                    'number': room.number,
                    'capacity': room.capacity,
                    'price_per_night': room.price_per_night
                })
        return available