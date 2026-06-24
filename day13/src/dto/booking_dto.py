# src/dto/booking_dto.py

from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional


class BookingCreateDTO(BaseModel):
    """DTO для создания бронирования."""
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date

    @field_validator('check_out')
    @classmethod
    def validate_dates(cls, v, info):
        if 'check_in' in info.data and v <= info.data['check_in']:
            raise ValueError('Дата выезда должна быть позже даты заезда')
        if (v - info.data['check_in']).days > 30:
            raise ValueError('Бронирование не может превышать 30 дней')
        return v


class BookingResponseDTO(BaseModel):
    """DTO для ответа с данными бронирования."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    room_id: int
    guest_name: str
    guest_email: str
    check_in: date
    check_out: date
    total_price: float
    status: str
    created_at: datetime


class BookingUpdateDTO(BaseModel):
    """DTO для обновления бронирования."""
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None