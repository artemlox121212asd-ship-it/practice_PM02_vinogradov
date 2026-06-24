"""
Фикстуры для интеграционных тестов (SQLAlchemy 1.4 compatible).
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import Base
from app.repositories import OrderRepository


@pytest.fixture(scope="function")
def db_session():
    """
    Фикстура для создания in-memory SQLite базы данных.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    session.begin_nested()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def repository(db_session: Session):
    """Фикстура для создания репозитория."""
    return OrderRepository(db_session)


@pytest.fixture(scope="function")
def sample_order_data():
    """Фикстура с данными для создания тестового заказа."""
    return {
        "customer_name": "Иван Петров",
        "delivery_address": "г. Москва, ул. Тверская, д. 1",
        "status": "PENDING",
        "items": [
            {"product_name": "Ноутбук", "quantity": 1, "price": 50000.0},
            {"product_name": "Мышь", "quantity": 2, "price": 1500.0},
            {"product_name": "Клавиатура", "quantity": 1, "price": 3000.0},
        ]
    }


@pytest.fixture(scope="function")
def sample_order(repository, sample_order_data):
    """Фикстура, создающая тестовый заказ в БД."""
    return repository.create(sample_order_data)