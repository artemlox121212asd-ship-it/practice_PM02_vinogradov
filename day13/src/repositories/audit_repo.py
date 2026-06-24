# src/repositories/audit_repo.py

from typing import List, Optional, Dict
from datetime import datetime
from src.domain.models import AuditLog, AuditAction
from src.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """In-Memory репозиторий аудит-логов с индексами."""

    def __init__(self):
        self._storage: Dict[int, AuditLog] = {}
        self._next_id = 1
        self._booking_index: Dict[int, List[int]] = {}
        self._user_index: Dict[int, List[int]] = {}

    def get_by_id(self, id: int) -> Optional[AuditLog]:
        return self._storage.get(id)

    def get_all(self, **filters) -> List[AuditLog]:
        result = list(self._storage.values())

        if 'booking_id' in filters:
            result = [a for a in result if a.booking_id == filters['booking_id']]
        if 'action' in filters:
            result = [a for a in result if a.action == filters['action']]
        if 'user_id' in filters:
            result = [a for a in result if a.user_id == filters['user_id']]
        if 'date_from' in filters:
            result = [a for a in result if a.timestamp >= filters['date_from']]
        if 'date_to' in filters:
            result = [a for a in result if a.timestamp <= filters['date_to']]

        result.sort(key=lambda x: x.timestamp, reverse=True)
        return result

    def add(self, log: AuditLog) -> AuditLog:
        log.id = self._next_id
        self._storage[log.id] = log
        self._next_id += 1

        if log.booking_id not in self._booking_index:
            self._booking_index[log.booking_id] = []
        self._booking_index[log.booking_id].append(log.id)

        if log.user_id:
            if log.user_id not in self._user_index:
                self._user_index[log.user_id] = []
            self._user_index[log.user_id].append(log.id)

        return log

    def update(self, entity: AuditLog) -> AuditLog:
        if entity.id not in self._storage:
            raise ValueError(f"AuditLog with id {entity.id} not found")
        self._storage[entity.id] = entity
        return entity

    def delete(self, id: int) -> bool:
        if id in self._storage:
            log = self._storage[id]
            if log.booking_id in self._booking_index:
                self._booking_index[log.booking_id] = [
                    i for i in self._booking_index[log.booking_id] if i != id
                ]
            if log.user_id and log.user_id in self._user_index:
                self._user_index[log.user_id] = [
                    i for i in self._user_index[log.user_id] if i != id
                ]
            del self._storage[id]
            return True
        return False

    def get_by_booking(self, booking_id: int) -> List[AuditLog]:
        """Получить историю изменений для конкретного бронирования."""
        if booking_id not in self._booking_index:
            return []
        return [self._storage[i] for i in self._booking_index[booking_id]]