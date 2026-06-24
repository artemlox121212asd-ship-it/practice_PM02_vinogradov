# app/repositories.py
"""
Репозиторий для работы с заказами.
"""

import httpx
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import Order, OrderItem
from app.exceptions import EntityNotFoundException, DeliveryCalculationException


class OrderRepository:
    """
    Репозиторий для управления заказами.
    """
    
    def __init__(self, session: Session):
        """
        Инициализация репозитория.
        
        Args:
            session: Сессия SQLAlchemy
        """
        self.session = session
    
    def create(self, order_data: Dict[str, Any]) -> Order:
        """
        Создаёт заказ и связанные позиции.
        
        Args:
            order_data: Словарь с данными заказа, должен содержать:
                - customer_name: str
                - delivery_address: str
                - status: str (опционально, по умолчанию 'PENDING')
                - items: List[Dict] с полями product_name, quantity, price
        
        Returns:
            Созданный объект Order
        """
        # Извлекаем позиции из данных
        items_data = order_data.pop('items', [])
        
        # Создаём заказ
        order = Order(**order_data)
        self.session.add(order)
        
        # Создаём позиции и добавляем их к заказу
        for item_data in items_data:
            item = OrderItem(**item_data)
            order.items.append(item)
        
        # Сохраняем в БД
        self.session.commit()
        self.session.refresh(order)
        
        return order
    
    def find_by_id(self, order_id: int) -> Optional[Order]:
        """
        Возвращает заказ по ID.
        
        Args:
            order_id: ID заказа
        
        Returns:
            Объект Order или None, если не найден
        """
        return self.session.query(Order).filter(Order.id == order_id).first()
    
    def find_all_by_status(self, status: str) -> List[Order]:
        """
        Возвращает список заказов с указанным статусом.
        
        Args:
            status: Статус заказа
        
        Returns:
            Список заказов
        """
        return self.session.query(Order).filter(Order.status == status).all()
    
    def update_status(self, order_id: int, new_status: str) -> Order:
        """
        Обновляет статус заказа.
        
        Args:
            order_id: ID заказа
            new_status: Новый статус
        
        Returns:
            Обновлённый объект Order
        
        Raises:
            EntityNotFoundException: Если заказ не найден
        """
        order = self.find_by_id(order_id)
        if order is None:
            raise EntityNotFoundException("Order", order_id)
        
        order.status = new_status
        self.session.commit()
        self.session.refresh(order)
        return order
    
    def delete(self, order_id: int) -> None:
        """
        Жёстко удаляет заказ и все его позиции.
        
        Args:
            order_id: ID заказа
        """
        order = self.find_by_id(order_id)
        if order:
            self.session.delete(order)
            self.session.commit()
    
    def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Order]:
        """
        Возвращает заказы в указанном временном интервале.
        
        Args:
            start_date: Начало интервала
            end_date: Конец интервала
        
        Returns:
            Список заказов
        """
        return (
            self.session.query(Order)
            .filter(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                )
            )
            .all()
        )
    
    def get_total_amount_for_order(self, order_id: int) -> float:
        """
        Вычисляет сумму всех позиций заказа через SQL-агрегацию.
        
        Args:
            order_id: ID заказа
        
        Returns:
            Общая сумма заказа
        """
        result = (
            self.session.query(
                func.sum(OrderItem.quantity * OrderItem.price).label('total')
            )
            .filter(OrderItem.order_id == order_id)
            .first()
        )
        
        return result[0] if result[0] is not None else 0.0
    
    def calculate_delivery_cost(self, order_id: int) -> float:
        """
        Рассчитывает стоимость доставки через внешний API.
        
        Args:
            order_id: ID заказа
        
        Returns:
            Стоимость доставки в рублях
        
        Raises:
            EntityNotFoundException: Если заказ не найден
            DeliveryCalculationException: При ошибке внешнего API
        """
        order = self.find_by_id(order_id)
        if order is None:
            raise EntityNotFoundException("Order", order_id)
        
        # Вычисляем общий вес позиций (каждая единица товара весит 0.5 кг)
        total_weight = 0.0
        for item in order.items:
            total_weight += item.quantity * 0.5
        
        # Формируем запрос к внешнему API
        request_body = {
            "address": order.delivery_address,
            "weight": total_weight
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    "https://api.delivery.com/calculate",
                    json=request_body
                )
                response.raise_for_status()
                data = response.json()
                
                # Проверяем наличие поля cost
                if "cost" not in data:
                    raise DeliveryCalculationException(
                        "Некорректный ответ от API доставки: отсутствует поле 'cost'"
                    )
                
                cost = data.get("cost")
                if cost is None:
                    raise DeliveryCalculationException(
                        "Некорректный ответ от API доставки: поле 'cost' имеет значение None"
                    )
                
                return float(cost)
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 400:
                raise DeliveryCalculationException(
                    f"Ошибка API доставки: статус {e.response.status_code}"
                )
            raise
        except httpx.RequestError as e:
            raise DeliveryCalculationException(f"Ошибка соединения с API доставки: {str(e)}")
        except ValueError as e:
            raise DeliveryCalculationException(f"Некорректный ответ от API доставки: {str(e)}")

# Добавляем для явного экспорта
__all__ = ['OrderRepository']