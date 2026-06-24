# src/config.py

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Config:
    """Конфигурация приложения."""
    
    seasonal_coefficients: Dict[int, float] = field(default_factory=lambda: {
        6: 1.2,   # июнь
        7: 1.5,   # июль
        8: 1.5,   # август
        12: 1.3,  # декабрь
        1: 1.1,   # январь
    })
    
    max_booking_days: int = 30
    long_stay_discount: float = 0.95
    extended_stay_discount: float = 0.9
    default_page_size: int = 100
    max_page_size: int = 500


config = Config()