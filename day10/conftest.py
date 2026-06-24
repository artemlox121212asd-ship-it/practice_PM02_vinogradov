import pytest
from datetime import datetime, date, timedelta
from fake_validator import FakeValidator

@pytest.fixture
def validator():
    return FakeValidator(chaos_mode=False)

@pytest.fixture
def chaos_validator():
    return FakeValidator(chaos_mode=True)

@pytest.fixture
def base_booking():
    return {
        "user_id": 1,
        "created_at": datetime(2025, 1, 1, 10, 0, 0),
        "booking_date": datetime.now(),
        "check_in": date.today() + timedelta(days=2),
        "check_out": date.today() + timedelta(days=5),
        "guests": 2,
        "children": 0,
        "child_seat": False,
        "total_amount": 30000.0,
        "phone_changed_at": None,
        "passport_country": "RU",
        "card_country": "RU"
    }

@pytest.fixture
def valid_bookings():
    today = date.today()
    return [
        {
            "user_id": 1,
            "created_at": datetime(2025, 1, 1, 10, 0, 0),
            "booking_date": datetime.now(),
            "check_in": today + timedelta(days=2),
            "check_out": today + timedelta(days=5),
            "guests": 2,
            "children": 0,
            "child_seat": False,
            "total_amount": 30000.0,
            "phone_changed_at": None,
            "passport_country": "RU",
            "card_country": "RU"
        },
        {
            "user_id": 2,
            "created_at": datetime(2024, 6, 1, 10, 0, 0),
            "booking_date": datetime.now(),
            "check_in": today + timedelta(days=3),
            "check_out": today + timedelta(days=7),
            "guests": 4,
            "children": 2,
            "child_seat": True,
            "total_amount": 45000.0,
            "phone_changed_at": None,
            "passport_country": "RU",
            "card_country": "RU"
        },
        {
            "user_id": 3,
            "created_at": datetime(2024, 1, 1, 10, 0, 0),
            "booking_date": datetime.now(),
            "check_in": today + timedelta(days=5),
            "check_out": today + timedelta(days=8),
            "guests": 1,
            "children": 0,
            "child_seat": False,
            "total_amount": 250000.0,
            "phone_changed_at": None,
            "passport_country": "RU",
            "card_country": "RU"
        }
    ]

@pytest.fixture
def invalid_bookings():
    today = date.today()
    return [
        {
            "user_id": 1,
            "created_at": datetime(2026, 6, 18, 10, 0, 0),
            "booking_date": datetime.now(),
            "check_in": today + timedelta(days=2),
            "check_out": today + timedelta(days=5),
            "guests": 2,
            "children": 0,
            "child_seat": False,
            "total_amount": 60000.0,
            "phone_changed_at": None,
            "passport_country": "RU",
            "card_country": "RU"
        },
        {
            "user_id": 2,
            "created_at": datetime(2024, 1, 1, 10, 0, 0),
            "booking_date": datetime.now(),
            "check_in": today + timedelta(days=2),
            "check_out": today + timedelta(days=5),
            "guests": 12,
            "children": 0,
            "child_seat": False,
            "total_amount": 30000.0,
            "phone_changed_at": None,
            "passport_country": "RU",
            "card_country": "RU"
        },
        {
            "user_id": 3,
            "created_at": datetime(2024, 1, 1, 10, 0, 0),
            "booking_date": datetime.now(),
            "check_in": today + timedelta(days=2),
            "check_out": today + timedelta(days=5),
            "guests": 3,
            "children": 2,
            "child_seat": False,
            "total_amount": 30000.0,
            "phone_changed_at": None,
            "passport_country": "RU",
            "card_country": "RU"
        },
        {
            "user_id": 4,
            "created_at": datetime(2024, 1, 1, 10, 0, 0),
            "booking_date": datetime.now(),
            "check_in": today,
            "check_out": today + timedelta(days=5),
            "guests": 2,
            "children": 0,
            "child_seat": False,
            "total_amount": 30000.0,
            "phone_changed_at": None,
            "passport_country": "RU",
            "card_country": "RU"
        },
        {
            "user_id": 5,
            "created_at": datetime(2024, 1, 1, 10, 0, 0),
            "booking_date": datetime.now(),
            "check_in": today + timedelta(days=2),
            "check_out": today + timedelta(days=35),
            "guests": 2,
            "children": 0,
            "child_seat": False,
            "total_amount": 30000.0,
            "phone_changed_at": None,
            "passport_country": "RU",
            "card_country": "RU"
        }
    ]

@pytest.fixture
def high_risk_booking():
    today = date.today()
    return {
        "user_id": 1,
        "created_at": datetime(2024, 1, 1, 10, 0, 0),
        "booking_date": datetime.now(),
        "check_in": today + timedelta(days=2),
        "check_out": today + timedelta(days=5),
        "guests": 2,
        "children": 0,
        "child_seat": False,
        "total_amount": 250000.0,
        "phone_changed_at": datetime.now() - timedelta(minutes=30),
        "passport_country": "RU",
        "card_country": "US"
    }

@pytest.fixture
def current_time():
    return datetime.now()

@pytest.fixture
def fixed_time():
    return datetime(2026, 6, 20, 12, 0, 0)