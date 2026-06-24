# src/dto/audit_dto.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
from src.domain.models import AuditAction


class AuditLogDTO(BaseModel):
    """DTO для аудит-лога."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    booking_id: int
    action: str
    user_id: Optional[int]
    user_role: str
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]


class AuditFilterDTO(BaseModel):
    """DTO для фильтрации аудит-логов."""
    booking_id: Optional[int] = None
    action: Optional[AuditAction] = None
    user_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 100
    offset: int = 0