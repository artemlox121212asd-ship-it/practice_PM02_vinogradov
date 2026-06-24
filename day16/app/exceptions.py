"""
Пользовательские исключения для приложения.
"""

class EntityNotFoundException(Exception):
    """Исключение, выбрасываемое когда сущность не найдена в БД."""
    def __init__(self, entity_type: str, entity_id: int):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} с ID {entity_id} не найден(а)")


class DeliveryCalculationException(Exception):
    """Исключение при ошибке расчёта стоимости доставки."""
    def __init__(self, message: str = "Ошибка при расчёте стоимости доставки"):
        super().__init__(message)