# app/models.py
"""
Models SQLAlchemy for the application.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column, Integer, String, DateTime, Float, ForeignKey, 
    CheckConstraint, func
)
# Change this import
from sqlalchemy.orm import declarative_base, relationship, validates

Base = declarative_base()


class Order(Base):
    """Модель заказа."""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20), nullable=False, default="PENDING")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    customer_name = Column(String(100), nullable=False)
    delivery_address = Column(String(200), nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)
    
    # Связь с позициями заказа (one-to-many)
    items = relationship(
        "OrderItem", 
        back_populates="order", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Ограничения на допустимые статусы
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'PAID', 'SHIPPED', 'CANCELLED')",
            name="check_status_valid"
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="check_total_amount_non_negative"
        ),
    )
    
    @validates('status')
    def validate_status(self, key, value):
        """Валидатор статуса."""
        allowed = {'PENDING', 'PAID', 'SHIPPED', 'CANCELLED'}
        if value not in allowed:
            raise ValueError(f"Недопустимый статус: {value}. Допустимы: {allowed}")
        return value
    
    def __repr__(self):
        return f"<Order(id={self.id}, status='{self.status}', customer='{self.customer_name}')>"


class OrderItem(Base):
    """Модель позиции заказа."""
    
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    # Связь с заказом
    order = relationship("Order", back_populates="items")
    
    # Ограничения
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        CheckConstraint("price >= 0", name="check_price_non_negative"),
    )
    
    @validates('quantity')
    def validate_quantity(self, key, value):
        """Валидатор количества."""
        if value <= 0:
            raise ValueError("Количество должно быть положительным числом")
        return value
    
    @validates('price')
    def validate_price(self, key, value):
        """Валидатор цены."""
        if value < 0:
            raise ValueError("Цена не может быть отрицательной")
        return value
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, product='{self.product_name}', qty={self.quantity})>"