class DomainError(Exception):
    """Базовое доменное исключение"""
    pass


class ValidationError(DomainError):
    """Ошибка валидации данных"""
    pass


class NotFoundError(DomainError):
    """Сущность не найдена"""
    pass


class BoardNotFoundError(NotFoundError):
    pass


class ColumnNotFoundError(NotFoundError):
    pass


class TaskNotFoundError(NotFoundError):
    pass


class TagNotFoundError(NotFoundError):
    pass


class BusinessRuleViolation(DomainError):
    """Нарушение бизнес-правила"""
    pass


class InvalidTaskStatusTransition(BusinessRuleViolation):
    """Некорректный переход статуса задачи"""
    pass


class ColumnPositionError(BusinessRuleViolation):
    """Ошибка позиции колонки"""
    pass