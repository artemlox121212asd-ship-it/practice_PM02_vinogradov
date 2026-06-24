# tests/test_audit_service.py

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock

from src.dto.booking_dto import BookingCreateDTO, BookingUpdateDTO
from src.dto.audit_dto import AuditFilterDTO
from src.domain.models import Booking, BookingStatus, AuditAction, AuditLog, Room
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
def sample_room():
    """Пример номера для тестов."""
    return Room(
        id=1,
        hotel_id=1,
        number="101",
        capacity=2,
        price_per_night=100.0,
        is_active=True
    )


def test_audit_on_booking_create(booking_service, mock_uow, sample_room):
    """Проверка создания записи аудита при создании бронирования."""
    dto = BookingCreateDTO(
        room_id=1,
        guest_name="John Doe",
        guest_email="john@example.com",
        check_in=date(2026, 6, 15),
        check_out=date(2026, 6, 20)
    )

    mock_uow.rooms.get_by_id.return_value = sample_room
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

    result = booking_service.create(dto)

    # Проверяем что аудит был создан
    mock_uow.audits.add.assert_called_once()
    audit_call_args = mock_uow.audits.add.call_args[0][0]

    assert audit_call_args.action == AuditAction.CREATE
    assert audit_call_args.booking_id == 1
    assert audit_call_args.user_id == 1


def test_audit_on_booking_cancel(booking_service, mock_uow):
    """Проверка создания записи аудита при отмене бронирования."""
    booking = Booking(
        id=1, room_id=1, guest_name="John", guest_email="john@example.com",
        check_in=date(2026, 6, 15), check_out=date(2026, 6, 20),
        total_price=500.0, status=BookingStatus.PENDING
    )
    mock_uow.bookings.get_by_id.return_value = booking
    # Очищаем историю вызовов перед тестом
    mock_uow.commit.reset_mock()

    booking_service.cancel(1)

    mock_uow.audits.add.assert_called_once()
    audit_call_args = mock_uow.audits.add.call_args[0][0]

    assert audit_call_args.action == AuditAction.CANCEL
    assert audit_call_args.booking_id == 1
    assert audit_call_args.old_values.get('status') == 'pending'
    assert audit_call_args.new_values.get('status') == 'cancelled'


def test_audit_on_booking_confirm(booking_service, mock_uow):
    """Проверка создания записи аудита при подтверждении бронирования."""
    booking = Booking(
        id=1, room_id=1, guest_name="John", guest_email="john@example.com",
        check_in=date(2026, 6, 15), check_out=date(2026, 6, 20),
        total_price=500.0, status=BookingStatus.PENDING
    )
    mock_uow.bookings.get_by_id.return_value = booking
    mock_uow.commit.reset_mock()

    booking_service.confirm(1)

    mock_uow.audits.add.assert_called_once()
    audit_call_args = mock_uow.audits.add.call_args[0][0]

    assert audit_call_args.action == AuditAction.CONFIRM
    assert audit_call_args.booking_id == 1
    assert audit_call_args.old_values.get('status') == 'pending'
    assert audit_call_args.new_values.get('status') == 'confirmed'


def test_audit_on_booking_update(booking_service, mock_uow):
    """Проверка создания записи аудита при обновлении бронирования."""
    booking = Booking(
        id=1, room_id=1, guest_name="John", guest_email="john@example.com",
        check_in=date(2026, 6, 15), check_out=date(2026, 6, 20),
        total_price=500.0, status=BookingStatus.PENDING
    )
    mock_uow.bookings.get_by_id.return_value = booking
    mock_uow.commit.reset_mock()

    dto = BookingUpdateDTO(guest_name="Jane Smith")

    booking_service.update(1, dto)

    mock_uow.audits.add.assert_called_once()
    audit_call_args = mock_uow.audits.add.call_args[0][0]

    assert audit_call_args.action == AuditAction.UPDATE
    assert audit_call_args.booking_id == 1
    assert audit_call_args.old_values.get('guest_name') == 'John'
    assert audit_call_args.new_values.get('guest_name') == 'Jane Smith'


def test_get_booking_history(booking_service, mock_uow):
    """Проверка получения истории изменений бронирования."""
    mock_logs = [
        AuditLog(
            id=1, booking_id=1, action=AuditAction.CREATE,
            user_id=1, user_role='admin',
            old_values={}, new_values={'status': 'pending'},
            timestamp=datetime.now()
        ),
        AuditLog(
            id=2, booking_id=1, action=AuditAction.CONFIRM,
            user_id=1, user_role='admin',
            old_values={'status': 'pending'}, new_values={'status': 'confirmed'},
            timestamp=datetime.now() + timedelta(minutes=5)
        )
    ]
    mock_uow.audits.get_by_booking.return_value = mock_logs

    history = booking_service.get_booking_history(1)

    assert len(history) == 2
    assert history[0].action == 'create'
    assert history[1].action == 'confirm'
    mock_uow.audits.get_by_booking.assert_called_once_with(1)


def test_search_audit_logs(booking_service, mock_uow):
    """Проверка поиска аудит-логов с фильтрацией."""
    mock_logs = [
        AuditLog(
            id=1, booking_id=1, action=AuditAction.CREATE,
            user_id=1, user_role='admin',
            old_values={}, new_values={'status': 'pending'},
            timestamp=datetime.now()
        )
    ]
    mock_uow.audits.get_all.return_value = mock_logs

    filters = AuditFilterDTO(booking_id=1, action=AuditAction.CREATE)
    audit_service = booking_service.audit_service

    logs = audit_service.search(filters)

    assert len(logs) == 1
    mock_uow.audits.get_all.assert_called_once_with(
        booking_id=1,
        action=AuditAction.CREATE,
        user_id=None,
        date_from=None,
        date_to=None
    )