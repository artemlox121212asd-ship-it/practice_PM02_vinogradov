# tests/test_booking_service.py

import pytest
from datetime import date
from unittest.mock import Mock

from src.services.booking_service import BookingService
from src.services.pricing_service import PricingService
from src.dto.booking_dto import BookingCreateDTO, BookingUpdateDTO
from src.domain.models import Room, Booking, BookingStatus
from src.domain.exceptions import (
    RoomNotFoundError,
    BookingConflictError,
    BookingNotFoundError,
    DomainError
)
from src.uow.unit_of_work import UnitOfWork


@pytest.fixture
def mock_uow():
    uow = Mock(spec=UnitOfWork)
    uow.bookings = Mock()
    uow.rooms = Mock()
    uow.audits = Mock()
    uow.commit = Mock()
    return uow


@pytest.fixture
def booking_service(mock_uow):
    pricing = PricingService()
    service = BookingService(mock_uow, pricing)
    service.set_user_context(1, 'admin')
    return service


def test_create_booking_success(booking_service, mock_uow):
    """Тест успешного создания бронирования."""
    dto = BookingCreateDTO(
        room_id=1,
        guest_name="John Doe",
        guest_email="john@example.com",
        check_in=date(2026, 6, 15),
        check_out=date(2026, 6, 20)
    )

    mock_room = Room(id=1, hotel_id=1, number="101", capacity=2, price_per_night=100.0)
    mock_uow.rooms.get_by_id.return_value = mock_room
    mock_uow.bookings.get_by_room_and_dates.return_value = []

    created_booking = Booking(
        id=1, room_id=1, guest_name="John Doe",
        guest_email="john@example.com",
        check_in=date(2026, 6, 15),
        check_out=date(2026, 6, 20),
        total_price=500.0,
        status=BookingStatus.PENDING
    )
    mock_uow.bookings.add.return_value = created_booking

    # Очищаем историю вызовов перед тестом
    mock_uow.commit.reset_mock()

    result = booking_service.create(dto)

    assert result.id == 1
    assert result.guest_name == "John Doe"
    mock_uow.bookings.add.assert_called_once()
    # Проверяем что commit вызван ровно 1 раз
    mock_uow.commit.assert_called_once()


def test_create_booking_room_not_found(booking_service, mock_uow):
    """Тест ошибки при создании бронирования для несуществующего номера."""
    dto = BookingCreateDTO(
        room_id=999,
        guest_name="Jane Doe",
        guest_email="jane@example.com",
        check_in=date(2026, 6, 15),
        check_out=date(2026, 6, 20)
    )

    mock_uow.rooms.get_by_id.return_value = None

    with pytest.raises(RoomNotFoundError):
        booking_service.create(dto)


def test_create_booking_conflict(booking_service, mock_uow):
    """Тест ошибки при конфликте бронирований."""
    dto = BookingCreateDTO(
        room_id=1,
        guest_name="John Doe",
        guest_email="john@example.com",
        check_in=date(2026, 6, 15),
        check_out=date(2026, 6, 20)
    )

    mock_room = Room(id=1, hotel_id=1, number="101", capacity=2, price_per_night=100.0)
    mock_uow.rooms.get_by_id.return_value = mock_room

    existing_booking = Booking(
        id=5, room_id=1, guest_name="Other",
        guest_email="other@example.com",
        check_in=date(2026, 6, 16),
        check_out=date(2026, 6, 18),
        total_price=200.0,
        status=BookingStatus.PENDING
    )
    mock_uow.bookings.get_by_room_and_dates.return_value = [existing_booking]

    with pytest.raises(BookingConflictError):
        booking_service.create(dto)


def test_cancel_booking_success(booking_service, mock_uow):
    """Тест успешной отмены бронирования."""
    booking = Booking(
        id=1, room_id=1, guest_name="John", guest_email="john@example.com",
        check_in=date(2026, 6, 15), check_out=date(2026, 6, 20),
        total_price=500.0, status=BookingStatus.PENDING
    )
    mock_uow.bookings.get_by_id.return_value = booking
    
    # Очищаем историю вызовов перед тестом
    mock_uow.commit.reset_mock()

    result = booking_service.cancel(1)

    assert result is True
    assert booking.status == BookingStatus.CANCELLED
    mock_uow.bookings.update.assert_called_once()
    mock_uow.commit.assert_called_once()


def test_cancel_booking_not_found(booking_service, mock_uow):
    """Тест ошибки при отмене несуществующего бронирования."""
    mock_uow.bookings.get_by_id.return_value = None

    with pytest.raises(BookingNotFoundError):
        booking_service.cancel(999)


def test_confirm_booking_success(booking_service, mock_uow):
    """Тест успешного подтверждения бронирования."""
    booking = Booking(
        id=1, room_id=1, guest_name="John", guest_email="john@example.com",
        check_in=date(2026, 6, 15), check_out=date(2026, 6, 20),
        total_price=500.0, status=BookingStatus.PENDING
    )
    mock_uow.bookings.get_by_id.return_value = booking
    
    # Очищаем историю вызовов перед тестом
    mock_uow.commit.reset_mock()

    booking_service.confirm(1)

    assert booking.status == BookingStatus.CONFIRMED
    mock_uow.bookings.update.assert_called_once()
    mock_uow.commit.assert_called_once()


def test_confirm_booking_wrong_status(booking_service, mock_uow):
    """Тест ошибки при подтверждении бронирования в неправильном статусе."""
    booking = Booking(
        id=1, room_id=1, guest_name="John", guest_email="john@example.com",
        check_in=date(2026, 6, 15), check_out=date(2026, 6, 20),
        total_price=500.0, status=BookingStatus.CONFIRMED
    )
    mock_uow.bookings.get_by_id.return_value = booking

    with pytest.raises(DomainError):
        booking_service.confirm(1)


def test_get_available_rooms(booking_service, mock_uow):
    """Тест получения доступных номеров."""
    check_in = date(2026, 6, 15)
    check_out = date(2026, 6, 20)

    room1 = Room(id=1, hotel_id=1, number="101", capacity=2, price_per_night=100.0)
    room2 = Room(id=2, hotel_id=1, number="102", capacity=4, price_per_night=150.0)
    mock_uow.rooms.get_by_hotel.return_value = [room1, room2]

    existing_booking = Booking(
        id=5, room_id=1, guest_name="Other",
        guest_email="other@example.com",
        check_in=date(2026, 6, 16),
        check_out=date(2026, 6, 18),
        total_price=200.0,
        status=BookingStatus.PENDING
    )

    def mock_get_by_room_and_dates(room_id, ci, co):
        if room_id == 1:
            return [existing_booking]
        return []

    mock_uow.bookings.get_by_room_and_dates.side_effect = mock_get_by_room_and_dates

    available = booking_service.get_available_rooms(1, check_in, check_out)

    assert len(available) == 1
    assert available[0]['room_id'] == 2