from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional

class BookingInput(BaseModel):
    user_id: int = Field(gt=0)
    created_at: datetime
    booking_date: datetime
    check_in: date
    check_out: date
    guests: int = Field(gt=0, le=10)
    children: int = Field(ge=0)
    child_seat: bool = False
    total_amount: float = Field(gt=0, le=1_000_000)
    phone_changed_at: Optional[datetime] = None
    passport_country: str = Field(min_length=2, max_length=2, pattern=r'^[A-Z]{2}$')
    card_country: str = Field(min_length=2, max_length=2, pattern=r'^[A-Z]{2}$')

    @field_validator('check_out')
    def validate_dates(cls, v, info):
        if 'check_in' in info.data:
            nights = (v - info.data['check_in']).days
            if not (1 <= nights <= 30):
                raise ValueError('Продолжительность от 1 до 30 ночей')
        return v

class BookingResult(BaseModel):
    valid: bool
    reasons: list[str] = Field(default_factory=list)
    risk_score: float = Field(ge=0, le=1)