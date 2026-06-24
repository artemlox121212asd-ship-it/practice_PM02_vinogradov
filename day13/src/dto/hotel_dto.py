# src/dto/hotel_dto.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class HotelCreateDTO(BaseModel):
    """DTO для создания отеля."""
    name: str
    address: str
    phone: str
    rating: Optional[float] = 0.0


class HotelResponseDTO(BaseModel):
    """DTO для ответа с данными отеля."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    address: str
    phone: str
    rating: float
    created_at: datetime


class HotelUpdateDTO(BaseModel):
    """DTO для обновления отеля."""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None