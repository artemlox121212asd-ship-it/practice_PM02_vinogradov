import random
from datetime import datetime, timedelta, date
from typing import Dict, Any
from pydantic import ValidationError
from models import BookingInput

class FakeValidator:
    def __init__(self, chaos_mode: bool = False):
        self.chaos_mode = chaos_mode

    def validate_booking(self, booking: Dict[str, Any]) -> Dict[str, Any]:
        if self.chaos_mode and random.random() < 0.05:
            return {
                "valid": random.choice([True, False]),
                "reasons": ["CHAOS_MODE"] if random.random() > 0.5 else [],
                "risk_score": random.uniform(0, 1)
            }

        reasons = []
        risk_score = 0.0

        # Сначала проверяем бизнес-правила (без Pydantic)
        # Правило 1: Сумма
        total_amount = booking.get("total_amount", 0)
        amount_valid = (0 < total_amount < 1_000_000)
        if not amount_valid:
            reasons.append("Сумма должна быть > 0 и < 1_000_000")

        # Правило 2: Новые пользователи
        created_at = booking.get("created_at")
        if created_at and isinstance(created_at, datetime):
            days_old = (datetime.now() - created_at).days
            if days_old < 7 and total_amount > 50_000:
                reasons.append("Для новых пользователей (менее 7 дней) сумма ≤ 50_000")

        # Правило 3: Количество гостей
        guests = booking.get("guests", 0)
        if guests > 10:
            reasons.append("Количество гостей не может превышать 10")

        # Правило 4: Дети и кресло
        children = booking.get("children", 0)
        child_seat = booking.get("child_seat", False)
        if children > 0 and not child_seat:
            reasons.append("При наличии детей требуется детское кресло")

        # Правило 5: Даты
        check_in = booking.get("check_in")
        check_out = booking.get("check_out")
        if check_in and isinstance(check_in, date):
            today = datetime.now().date()
            if check_in <= today:
                reasons.append("Заезд должен быть не раньше завтрашнего дня")
        
        if check_in and check_out and isinstance(check_in, date) and isinstance(check_out, date):
            nights = (check_out - check_in).days
            if not (1 <= nights <= 30):
                reasons.append("Продолжительность бронирования должна быть от 1 до 30 ночей")

        # Проверяем Pydantic валидацию и добавляем ошибки
        try:
            data = BookingInput(**booking)
        except ValidationError as e:
            # Добавляем ошибки Pydantic к причинам
            for error in e.errors():
                field = error['loc'][0]
                msg = error['msg']
                reasons.append(f"{field}: {msg}")
            
            # Если есть ошибки Pydantic, заказ невалиден
            return {
                "valid": False,
                "reasons": reasons,
                "risk_score": 0.0
            }

        # Если Pydantic прошел, используем data для дальнейших проверок
        # Правило 6: Риск-скоринг (только если заказ валиден по всем правилам)
        if len(reasons) == 0:
            if data.total_amount > 200_000:
                risk_score = 0.8
            
            if data.phone_changed_at:
                seconds_since = (datetime.now() - data.phone_changed_at).total_seconds()
                if seconds_since < 3600:
                    risk_score = min(1.0, risk_score + 0.2)
            
            if data.passport_country != data.card_country:
                risk_score = min(1.0, risk_score + 0.3)

        valid = len(reasons) == 0
        
        return {
            "valid": valid,
            "reasons": reasons,
            "risk_score": risk_score
        }