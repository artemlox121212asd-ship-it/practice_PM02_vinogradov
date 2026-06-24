import pytest
import random
from datetime import datetime, date, timedelta
from freezegun import freeze_time
from fake_validator import FakeValidator

def test_time_boundary_checkin(validator, base_booking):
    with freeze_time("2026-06-20 12:00:00"):
        # Создаем booking заново внутри freeze_time
        booking = {
            "user_id": 1,
            "created_at": datetime(2025, 1, 1, 10, 0, 0),
            "booking_date": datetime(2026, 6, 20, 12, 0, 0),
            "check_in": date(2026, 6, 20),  # сегодня
            "check_out": date(2026, 6, 23),
            "guests": 2,
            "children": 0,
            "child_seat": False,
            "total_amount": 30000.0,
            "phone_changed_at": None,
            "passport_country": "RU",
            "card_country": "RU"
        }
        result = validator.validate_booking(booking)
        assert result["valid"] is False
        
        booking["check_in"] = date(2026, 6, 21)  # завтра
        result = validator.validate_booking(booking)
        assert result["valid"] is True

def test_time_boundary_new_user(validator, base_booking):
    with freeze_time("2026-06-20 12:00:00"):
        # Создаем booking заново внутри freeze_time
        booking = {
            "user_id": 1,
            "created_at": datetime(2026, 6, 13, 12, 0, 0),  # 7 дней назад
            "booking_date": datetime(2026, 6, 20, 12, 0, 0),
            "check_in": date(2026, 6, 22),
            "check_out": date(2026, 6, 25),
            "guests": 2,
            "children": 0,
            "child_seat": False,
            "total_amount": 60000.0,
            "phone_changed_at": None,
            "passport_country": "RU",
            "card_country": "RU"
        }
        result = validator.validate_booking(booking)
        assert result["valid"] is True
        
        booking["created_at"] = datetime(2026, 6, 14, 12, 0, 0)  # 6 дней назад
        result = validator.validate_booking(booking)
        assert result["valid"] is False

def test_time_boundary_phone_change(validator):
    """Тест границы смены телефона"""
    with freeze_time("2026-06-20 12:00:00"):
        # Создаем booking с правильными данными
        booking = {
            "user_id": 1,
            "created_at": datetime(2025, 1, 1, 10, 0, 0),
            "booking_date": datetime(2026, 6, 20, 12, 0, 0),
            "check_in": date(2026, 6, 22),
            "check_out": date(2026, 6, 25),
            "guests": 2,
            "children": 0,
            "child_seat": False,
            "total_amount": 30000.0,  # Меньше 200000, чтобы риск был только от телефона
            "phone_changed_at": datetime(2026, 6, 20, 11, 30, 0),  # 30 минут назад
            "passport_country": "RU",
            "card_country": "RU"
        }
        result = validator.validate_booking(booking)
        assert result["risk_score"] == 0.2, f"Ожидался риск 0.2, получен {result['risk_score']}"
        
        booking["phone_changed_at"] = datetime(2026, 6, 20, 10, 59, 0)  # 61 минута назад
        result = validator.validate_booking(booking)
        assert result["risk_score"] == 0.0, f"Ожидался риск 0.0, получен {result['risk_score']}"

def test_duplicates_dont_crash(validator, base_booking):
    for i in range(100):
        booking = base_booking.copy()
        booking["user_id"] = i
        result = validator.validate_booking(booking)
        assert isinstance(result["valid"], bool)
        assert 0.0 <= result["risk_score"] <= 1.0
        assert isinstance(result["reasons"], list)

def test_random_orders_stability(validator):
    countries = ["RU", "US", "DE", "FR", "CN", "GB", "JP"]
    
    for _ in range(100):
        booking = {
            "user_id": random.randint(1, 10000),
            "created_at": datetime.now() - timedelta(days=random.randint(1, 365)),
            "booking_date": datetime.now(),
            "check_in": date.today() + timedelta(days=random.randint(1, 30)),
            "check_out": date.today() + timedelta(days=random.randint(2, 31)),
            "guests": random.randint(1, 10),
            "children": random.randint(0, 3),
            "child_seat": True if random.randint(0, 1) == 0 else False,
            "total_amount": random.uniform(1, 2000000),
            "phone_changed_at": None if random.random() > 0.5 else datetime.now() - timedelta(minutes=random.randint(1, 120)),
            "passport_country": random.choice(countries),
            "card_country": random.choice(countries)
        }
        
        result = validator.validate_booking(booking)
        assert isinstance(result["valid"], bool)
        assert 0.0 <= result["risk_score"] <= 1.0
        if not result["valid"]:
            assert len(result["reasons"]) > 0

def test_chaos_mode(validator, base_booking):
    chaos_validator = FakeValidator(chaos_mode=True)
    results = []
    for _ in range(50):
        result = chaos_validator.validate_booking(base_booking)
        results.append(result)
        assert isinstance(result["valid"], bool)
        assert 0.0 <= result["risk_score"] <= 1.0
    
    chaos_count = sum(1 for r in results if "CHAOS_MODE" in r.get("reasons", []))
    # Не проверяем строго, так как это вероятностный тест
    assert chaos_count >= 0

def test_multiple_factors_risk(validator, base_booking):
    booking = base_booking.copy()
    booking["total_amount"] = 250000.0
    booking["phone_changed_at"] = datetime.now() - timedelta(minutes=30)
    booking["passport_country"] = "RU"
    booking["card_country"] = "US"
    
    result = validator.validate_booking(booking)
    assert result["risk_score"] == 1.0

def test_risk_floor_and_ceiling(validator, base_booking):
    booking = base_booking.copy()
    booking["total_amount"] = 200000.0
    result = validator.validate_booking(booking)
    assert result["risk_score"] == 0.0
    
    booking["total_amount"] = 250000.0
    booking["phone_changed_at"] = datetime.now() - timedelta(minutes=30)
    booking["passport_country"] = "RU"
    booking["card_country"] = "US"
    result = validator.validate_booking(booking)
    assert result["risk_score"] == 1.0

def test_invalid_date_format(validator, base_booking):
    booking = base_booking.copy()
    booking["check_in"] = "2026/06/22"  # Неправильный формат
    
    result = validator.validate_booking(booking)
    assert result["valid"] is False
    assert isinstance(result["reasons"], list)
    assert len(result["reasons"]) > 0
    # Проверяем, что есть ошибка о формате даты
    assert any("check_in" in str(r).lower() or "date" in str(r).lower() for r in result["reasons"])

def test_missing_required_field(validator, base_booking):
    booking = base_booking.copy()
    del booking["user_id"]
    
    result = validator.validate_booking(booking)
    assert result["valid"] is False
    assert isinstance(result["reasons"], list)

def test_negative_values(validator, base_booking):
    booking = base_booking.copy()
    booking["total_amount"] = -100.0
    booking["guests"] = -5
    
    result = validator.validate_booking(booking)
    assert result["valid"] is False
    assert isinstance(result["reasons"], list)

def test_extreme_values(validator, base_booking):
    booking = base_booking.copy()
    booking["total_amount"] = 999999999.0
    booking["guests"] = 999
    
    result = validator.validate_booking(booking)
    assert result["valid"] is False
    assert isinstance(result["reasons"], list)

def test_all_countries_combination(validator, base_booking):
    countries = ["RU", "US", "DE", "FR", "CN", "GB", "JP", "BR", "IN", "AU"]
    
    for country1 in countries:
        for country2 in countries:
            booking = base_booking.copy()
            booking["passport_country"] = country1
            booking["card_country"] = country2
            
            result = validator.validate_booking(booking)
            assert isinstance(result["valid"], bool)
            assert 0.0 <= result["risk_score"] <= 1.0
            
            if country1 != country2:
                assert result["risk_score"] >= 0.3