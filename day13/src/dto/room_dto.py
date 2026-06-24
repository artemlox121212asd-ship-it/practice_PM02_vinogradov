# src/dto/room_dto.py

from pydantic import BaseModel, ConfigDict
from typing import Optional


class RoomCreateDTO(BaseModel):
    """DTO для создания номера."""
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    room_type: str = "standard"


class RoomResponseDTO(BaseModel):
    """DTO для ответа с данными номера."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    hotel_id: int
    number: str
    capacity: int
    price_per_night: float
    is_active: bool
    room_type: str


class RoomUpdateDTO(BaseModel):
    """DTO для обновления номера."""
    number: Optional[str] = None
    capacity: Optional[int] = None
    price_per_night: Optional[float] = None
    is_active: Optional[bool] = None
    room_type: Optional[str] = None