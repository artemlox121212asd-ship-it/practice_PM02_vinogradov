import pytest
from pydantic import ValidationError
from app.schemas import OrderCreateDTO

# Параметризованный тест: проверяем 10 номеров (5 валидных, 5 невалидных)
@pytest.mark.parametrize("phone, expected_valid", [
    # Валидные номера (разные форматы)
    ("+79991234567", True),      # +7 и 10 цифр
    ("89991234567", True),       # 8 и 10 цифр
    ("+7-999-123-45-67", True),  # +7 с дефисами
    ("8 (999) 123-45-67", True), # 8 со скобками и дефисами
    ("+7 999 123 45 67", True),  # +7 с пробелами

    # Невалидные номера
    ("123", False),              # слишком короткий
    ("abc", False),              # буквы
    ("+7999123456", False),      # не хватает цифры (9 цифр)
    ("899912345678", False),     # слишком длинный (11 цифр после 8)
    ("+7(999)123-45-678", False) # лишняя цифра в конце
])
def test_phone_validation(phone, expected_valid):
    """
    Тест проверяет валидацию номера телефона в OrderCreateDTO.
    - Если expected_valid=True, ожидаем успешное создание DTO.
    - Если expected_valid=False, ожидаем исключение ValidationError.
    """
    # Arrange: тестовый email (валидный всегда)
    valid_email = "test@example.com"

    # Act & Assert
    if expected_valid:
        # Проверяем, что DTO создается без ошибок
        dto = OrderCreateDTO(phone=phone, email=valid_email)
        # Дополнительная проверка: поле сохранилось как было (или очистилось от пробелов — по желанию)
        assert dto.phone == phone, "Номер телефона должен сохраниться без изменений"
    else:
        # Проверяем, что выбрасывается ValidationError
        with pytest.raises(ValidationError) as exc_info:
            OrderCreateDTO(phone=phone, email=valid_email)
        # Проверяем, что ошибка связана с полем phone
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'phone' for error in errors), "Ошибка должна быть о поле phone"