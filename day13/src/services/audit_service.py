# src/services/audit_service.py

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.domain.models import AuditLog, AuditAction
from src.dto.audit_dto import AuditLogDTO, AuditFilterDTO
from src.uow.unit_of_work import UnitOfWork


class AuditService:
    """Сервис для работы с аудит-логами."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def log_action(
        self,
        booking_id: int,
        action: AuditAction,
        user_id: Optional[int],
        user_role: str,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Создать запись аудита (без commit - commit делает вызывающий код)."""
        log = AuditLog(
            id=None,
            booking_id=booking_id,
            action=action,
            user_id=user_id,
            user_role=user_role,
            old_values=old_values,
            new_values=new_values,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        saved = self.uow.audits.add(log)
        # НЕ вызываем commit здесь! commit делает вызывающий метод
        return saved

    def get_booking_history(self, booking_id: int) -> List[AuditLogDTO]:
        """Получить историю изменений для бронирования."""
        logs = self.uow.audits.get_by_booking(booking_id)
        return [AuditLogDTO.model_validate(log) for log in logs]

    def search(self, filters: AuditFilterDTO) -> List[AuditLogDTO]:
        """Поиск аудит-логов по фильтрам с пагинацией."""
        logs = self.uow.audits.get_all(**filters.model_dump(exclude={'limit', 'offset'}))
        start = filters.offset
        end = start + filters.limit
        return [AuditLogDTO.model_validate(log) for log in logs[start:end]]

    def get_by_id(self, log_id: int) -> Optional[AuditLogDTO]:
        """Получить аудит-лог по ID."""
        log = self.uow.audits.get_by_id(log_id)
        if log:
            return AuditLogDTO.model_validate(log)
        return None