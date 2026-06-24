from pydantic import BaseModel, Field, EmailStr, validator
import re

class OrderCreateDTO(BaseModel):
    phone: str = Field(..., description="Номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX")
    email: EmailStr = Field(..., description="Email адрес")

    @validator('phone')
    def validate_phone(cls, value):
        # Регулярка для российских номеров: +7 или 8, затем 10 цифр (с дефисами и пробелами)
        pattern = r'^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
        if not re.match(pattern, value):
            raise ValueError('Invalid phone number format. Use +7XXXXXXXXXX or 8XXXXXXXXXX')
        return value