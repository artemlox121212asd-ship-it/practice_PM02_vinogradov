# tests/conftest.py

import sys
from pathlib import Path

# Добавляем корневую папку в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from unittest.mock import Mock

from src.services.pricing_service import PricingService
from src.services.booking_service import BookingService
from src.services.audit_service import AuditService
from src.uow.unit_of_work import UnitOfWork
from src.domain.models import Room, Booking, BookingStatus


@pytest.fixture
def mock_uow():
    """Мок Unit of Work."""
    uow = Mock(spec=UnitOfWork)
    uow.bookings = Mock()
    uow.rooms = Mock()
    uow.audits = Mock()
    uow.hotels = Mock()
    uow.commit = Mock()
    uow.rollback = Mock()
    return uow


@pytest.fixture
def pricing_service():
    """Экземпляр PricingService."""
    return PricingService()


@pytest.fixture
def booking_service(mock_uow, pricing_service):
    """Экземпляр BookingService с моками."""
    service = BookingService(mock_uow, pricing_service)
    service.set_user_context(1, 'admin')
    return service


@pytest.fixture
def audit_service(mock_uow):
    """Экземпляр AuditService с моками."""
    return AuditService(mock_uow)


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


@pytest.fixture
def sample_booking():
    """Пример бронирования для тестов."""
    from datetime import date
    return Booking(
        id=1,
        room_id=1,
        guest_name="John Doe",
        guest_email="john@example.com",
        check_in=date(2026, 6, 15),
        check_out=date(2026, 6, 20),
        total_price=500.0,
        status=BookingStatus.PENDING
    )