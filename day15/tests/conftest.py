"""
Глобальные фикстуры для всех тестов проекта.
"""
import pytest

# Убираем импорт app, чтобы не было ошибки
# from app.schemas import OrderCreateDTO  # УДАЛИТЬ!

@pytest.fixture
def valid_email():
    """Возвращает валидный email для тестов."""
    return "test@example.com"

@pytest.fixture
def valid_phone():
    """Возвращает валидный номер телефона."""
    return "+79991234567"

@pytest.fixture
def invalid_phone():
    """Возвращает невалидный номер телефона."""
    return "12345"

@pytest.fixture
def phone_test_cases():
    """
    Возвращает список кортежей (phone, expected_valid) для параметризации.
    """
    return [
        # Валидные номера
        ("+79991234567", True),
        ("89991234567", True),
        ("+7-999-123-45-67", True),
        ("8 (999) 123-45-67", True),
        ("+7 999 123 45 67", True),
        # Невалидные номера
        ("123", False),
        ("abc", False),
        ("+7999123456", False),
        ("899912345678", False),
        ("+7(999)123-45-678", False),
    ]

# Убираем все фикстуры, которые создают DTO
# valid_order_dto, order_dto_factory - удаляем или комментируем