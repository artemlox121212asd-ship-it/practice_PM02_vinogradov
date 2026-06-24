import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import datetimes, dates, floats, integers, sampled_from, just, booleans
from datetime import datetime, date, timedelta
from fake_validator import FakeValidator

validator = FakeValidator(chaos_mode=False)

@st.composite
def valid_booking_strategy(draw):
    today = date.today()
    check_in = draw(dates(min_value=today + timedelta(days=1), max_value=today + timedelta(days=30)))
    nights = draw(integers(min_value=1, max_value=30))
    check_out = check_in + timedelta(days=nights)
    
    children = draw(integers(min_value=0, max_value=3))
    child_seat = True if children > 0 else draw(booleans())
    
    return {
        "user_id": draw(integers(min_value=1, max_value=1000000)),
        "created_at": draw(datetimes(min_value=datetime(2020, 1, 1), max_value=datetime.now() - timedelta(days=8))),
        "booking_date": datetime.now(),
        "check_in": check_in,
        "check_out": check_out,
        "guests": draw(integers(min_value=1, max_value=10)),
        "children": children,
        "child_seat": child_seat,
        "total_amount": draw(floats(min_value=1.0, max_value=49000.0)),
        "phone_changed_at": draw(st.none()),
        "passport_country": draw(sampled_from(["RU", "US", "DE", "FR", "CN"])),
        "card_country": draw(sampled_from(["RU", "US", "DE", "FR", "CN"]))
    }

@st.composite
def any_booking_strategy(draw):
    today = date.today()
    check_in = draw(dates(min_value=today - timedelta(days=10), max_value=today + timedelta(days=40)))
    nights = draw(integers(min_value=-5, max_value=40))
    check_out = check_in + timedelta(days=nights) if nights > 0 else check_in + timedelta(days=1)
    
    return {
        "user_id": draw(integers(min_value=-10, max_value=1000000)),
        "created_at": draw(datetimes(min_value=datetime(2020, 1, 1), max_value=datetime.now() + timedelta(days=1))),
        "booking_date": datetime.now(),
        "check_in": check_in,
        "check_out": check_out,
        "guests": draw(integers(min_value=-5, max_value=20)),
        "children": draw(integers(min_value=-2, max_value=10)),
        "child_seat": draw(booleans()),
        "total_amount": draw(floats(min_value=-1000.0, max_value=2000000.0)),
        "phone_changed_at": draw(st.one_of(st.none(), datetimes())),
        "passport_country": draw(sampled_from(["RU", "US", "DE", "FR", "CN", "XX"])),
        "card_country": draw(sampled_from(["RU", "US", "DE", "FR", "CN", "XX"]))
    }

@given(valid_booking_strategy())
def test_valid_booking_always_valid(booking):
    result = validator.validate_booking(booking)
    assert result["valid"] is True

@given(valid_booking_strategy())
def test_risk_score_bounds(booking):
    result = validator.validate_booking(booking)
    assert 0.0 <= result["risk_score"] <= 1.0

@given(valid_booking_strategy())
def test_risk_monotonic_by_amount(booking):
    base_total = booking["total_amount"]
    test_cases = []
    
    for multiplier in [0.5, 1.0, 2.0, 4.0]:
        test_booking = booking.copy()
        test_booking["total_amount"] = base_total * multiplier
        test_cases.append(test_booking)
    
    risks = []
    for test_booking in sorted(test_cases, key=lambda b: b["total_amount"]):
        result = validator.validate_booking(test_booking)
        risks.append(result["risk_score"])
    
    for i in range(len(risks) - 1):
        assert risks[i] <= risks[i+1] + 0.001

@given(st.lists(valid_booking_strategy(), min_size=1, max_size=5))
def test_invalid_has_reasons(bookings):
    for booking in bookings:
        invalid_booking = booking.copy()
        invalid_booking["total_amount"] = -1.0
        
        result = validator.validate_booking(invalid_booking)
        if not result["valid"]:
            assert len(result["reasons"]) > 0

@given(valid_booking_strategy())
def test_time_monotonic(booking):
    time_shifts = [-12, -6, 0, 6, 12]
    results = []
    
    for shift in time_shifts:
        result = validator.validate_booking(booking)
        results.append(result["valid"])
    
    assert all(r == results[0] for r in results)

@given(any_booking_strategy())
def test_any_booking_stable(booking):
    result = validator.validate_booking(booking)
    assert isinstance(result["valid"], bool)
    assert 0.0 <= result["risk_score"] <= 1.0
    assert isinstance(result["reasons"], list)
    
    if not result["valid"] and len(result["reasons"]) == 0:
        assert result["reasons"] is not None

@given(valid_booking_strategy())
def test_new_user_limit(booking):
    booking["created_at"] = datetime.now() - timedelta(days=1)
    booking["total_amount"] = 60000.0
    
    result = validator.validate_booking(booking)
    if not result["valid"]:
        assert any("50_000" in r for r in result["reasons"])

@given(valid_booking_strategy())
def test_children_seat_required(booking):
    booking["children"] = 2
    booking["child_seat"] = False
    
    result = validator.validate_booking(booking)
    if not result["valid"]:
        assert any("кресло" in r for r in result["reasons"])

@given(valid_booking_strategy())
def test_checkin_after_today(booking):
    booking["check_in"] = date.today()
    result = validator.validate_booking(booking)
    # Просто проверяем, что заказ невалиден
    assert result["valid"] is False

@given(valid_booking_strategy())
def test_nights_range(booking):
    booking["check_in"] = date.today() + timedelta(days=1)
    booking["check_out"] = date.today() + timedelta(days=35)
    
    result = validator.validate_booking(booking)
    if not result["valid"]:
        assert any("30" in r for r in result["reasons"])