import pytest
from datetime import datetime, date, timedelta

@pytest.mark.parametrize("overrides,expected_valid,expected_risk_min,expected_risk_max,reasons_contain", [
    # Граничные значения суммы
    ({"total_amount": 0.01}, True, 0.0, 0.0, []),
    ({"total_amount": 999999.99}, True, 0.8, 0.8, []),
    ({"total_amount": 0.0}, False, 0.0, 0.0, ["0"]),
    ({"total_amount": 1000000.0}, False, 0.0, 0.0, ["1_000_000"]),
    ({"total_amount": -100.0}, False, 0.0, 0.0, ["0"]),
    ({"total_amount": 500000.0}, True, 0.8, 0.8, []),
    
    # Новые пользователи
    ({"created_at": datetime.now() - timedelta(days=6, hours=23), "total_amount": 50000}, True, 0.0, 0.0, []),
    ({"created_at": datetime.now() - timedelta(days=6, hours=23), "total_amount": 50001}, False, 0.0, 0.0, ["50_000"]),
    ({"created_at": datetime.now() - timedelta(days=7), "total_amount": 60000}, True, 0.0, 0.0, []),
    ({"created_at": datetime.now() - timedelta(days=1), "total_amount": 50000}, True, 0.0, 0.0, []),
    ({"created_at": datetime.now() - timedelta(days=1), "total_amount": 50001}, False, 0.0, 0.0, ["50_000"]),
    
    # Количество гостей
    ({"guests": 1}, True, 0.0, 0.0, []),
    ({"guests": 10}, True, 0.0, 0.0, []),
    ({"guests": 11}, False, 0.0, 0.0, ["10"]),
    ({"guests": 20}, False, 0.0, 0.0, ["10"]),
    
    # Дети и кресло
    ({"children": 1, "child_seat": True}, True, 0.0, 0.0, []),
    ({"children": 1, "child_seat": False}, False, 0.0, 0.0, ["кресло"]),
    ({"children": 0, "child_seat": False}, True, 0.0, 0.0, []),
    ({"children": 5, "child_seat": True}, True, 0.0, 0.0, []),
    
    # Даты заезда
    ({"check_in": date.today() + timedelta(days=1)}, True, 0.0, 0.0, []),
    ({"check_in": date.today()}, False, 0.0, 0.0, ["завтра"]),
    ({"check_in": date.today() - timedelta(days=1)}, False, 0.0, 0.0, ["завтра"]),
    
    # Продолжительность
    ({"check_out": date.today() + timedelta(days=2), "check_in": date.today() + timedelta(days=1)}, True, 0.0, 0.0, []),
    ({"check_in": date.today() + timedelta(days=1), "check_out": date.today() + timedelta(days=32)}, False, 0.0, 0.0, ["30"]),
    ({"check_out": date.today() + timedelta(days=1), "check_in": date.today() + timedelta(days=1)}, False, 0.0, 0.0, ["1"]),
    
    # Риск-скоринг
    ({"total_amount": 200000.01}, True, 0.8, 0.8, []),
    ({"total_amount": 200000.0}, True, 0.0, 0.0, []),
    ({"total_amount": 250000, "phone_changed_at": datetime.now() - timedelta(minutes=30)}, True, 1.0, 1.0, []),
    ({"total_amount": 250000, "phone_changed_at": datetime.now() - timedelta(hours=2)}, True, 0.8, 0.8, []),
    ({"total_amount": 250000, "passport_country": "RU", "card_country": "US"}, True, 1.0, 1.0, []),
    ({"total_amount": 250000, "passport_country": "US", "card_country": "US"}, True, 0.8, 0.8, []),
    ({"phone_changed_at": datetime.now() - timedelta(minutes=30)}, True, 0.2, 0.2, []),
    ({"phone_changed_at": datetime.now() - timedelta(minutes=61)}, True, 0.0, 0.0, []),
    ({"passport_country": "RU", "card_country": "US"}, True, 0.3, 0.3, []),
    ({"passport_country": "RU", "card_country": "RU"}, True, 0.0, 0.0, []),
    
    # Комбинации
    ({"total_amount": 250000, "phone_changed_at": datetime.now() - timedelta(minutes=30), "passport_country": "RU", "card_country": "US"}, True, 1.0, 1.0, []),
    # Исправлено: проверяем наличие хотя бы одной из причин
    ({"created_at": datetime.now() - timedelta(days=1), "total_amount": 60000, "guests": 11}, False, 0.0, 0.0, ["50_000", "10", "guests"]),
    ({"children": 2, "child_seat": False, "check_in": date.today()}, False, 0.0, 0.0, ["кресло", "завтра"]),
    ({"total_amount": 0, "guests": 11}, False, 0.0, 0.0, ["0", "10", "guests"]),
    ({"created_at": datetime.now() - timedelta(days=1), "children": 2, "child_seat": False}, False, 0.0, 0.0, ["кресло"]),
    ({"check_in": date.today() + timedelta(days=1), "check_out": date.today() + timedelta(days=32), "guests": 11}, False, 0.0, 0.0, ["10", "30", "guests"]),
])
def test_validate_booking(validator, base_booking, overrides, expected_valid, expected_risk_min, expected_risk_max, reasons_contain):
    booking = {**base_booking, **overrides}
    result = validator.validate_booking(booking)
    
    assert result["valid"] == expected_valid, f"Ожидался valid={expected_valid}, получен {result['valid']}. Причины: {result['reasons']}"
    assert expected_risk_min <= result["risk_score"] <= expected_risk_max, f"risk_score={result['risk_score']} вне диапазона [{expected_risk_min}, {expected_risk_max}]"
    
    for reason in reasons_contain:
        assert any(reason in r for r in result["reasons"]), f"Причина '{reason}' не найдена. Получены причины: {result['reasons']}"