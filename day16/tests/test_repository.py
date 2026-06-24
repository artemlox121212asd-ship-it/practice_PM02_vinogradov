"""
Интеграционные тесты для OrderRepository.
"""

import pytest
import json
import httpx
from datetime import datetime, timedelta

from app.exceptions import EntityNotFoundException, DeliveryCalculationException
from app.models import Order, OrderItem


class TestOrderRepository:
    """Тесты для OrderRepository."""
    
    def test_create_order(self, repository, sample_order_data):
        """Тест создания заказа с позициями."""
        order = repository.create(sample_order_data)
        
        assert order.id is not None
        assert order.customer_name == sample_order_data["customer_name"]
        assert order.delivery_address == sample_order_data["delivery_address"]
        assert order.status == "PENDING"
        assert len(order.items) == 3
        
        saved_order = repository.find_by_id(order.id)
        assert saved_order is not None
        assert saved_order.customer_name == sample_order_data["customer_name"]
        assert len(saved_order.items) == 3
    
    def test_find_by_id_existing(self, repository, sample_order):
        """Тест поиска существующего заказа по ID."""
        found = repository.find_by_id(sample_order.id)
        
        assert found is not None
        assert found.id == sample_order.id
        assert found.customer_name == sample_order.customer_name
    
    def test_find_by_id_not_existing(self, repository):
        """Тест поиска несуществующего заказа."""
        found = repository.find_by_id(99999)
        assert found is None
    
    @pytest.mark.parametrize("status", ["PENDING", "PAID", "SHIPPED", "CANCELLED"])
    def test_find_all_by_status(self, repository, sample_order_data, status):
        """Тест поиска заказов по статусу с параметризацией."""
        repository.create({**sample_order_data, "status": "PENDING"})
        repository.create({**sample_order_data, "status": "PAID"})
        repository.create({**sample_order_data, "status": "SHIPPED"})
        repository.create({**sample_order_data, "status": "CANCELLED"})
        
        if status == "PENDING":
            repository.create({**sample_order_data, "status": "PENDING"})
        
        result = repository.find_all_by_status(status)
        
        assert all(order.status == status for order in result)
        
        if status == "PENDING":
            assert len(result) == 2
        else:
            assert len(result) == 1
    
    def test_update_status_existing(self, repository, sample_order):
        """Тест обновления статуса существующего заказа."""
        new_status = "PAID"
        updated = repository.update_status(sample_order.id, new_status)
        
        assert updated.status == new_status
        assert updated.id == sample_order.id
        
        found = repository.find_by_id(sample_order.id)
        assert found.status == new_status
    
    def test_update_status_not_existing(self, repository):
        """Тест обновления статуса несуществующего заказа."""
        with pytest.raises(EntityNotFoundException) as exc_info:
            repository.update_status(99999, "PAID")
        
        assert "Order с ID 99999 не найден" in str(exc_info.value)
    
    def test_delete_order(self, repository, sample_order):
        """Тест удаления заказа и каскадного удаления позиций."""
        order_id = sample_order.id
        repository.delete(order_id)
        
        deleted = repository.find_by_id(order_id)
        assert deleted is None
        
        items = repository.session.query(OrderItem).filter(
            OrderItem.order_id == order_id
        ).all()
        assert len(items) == 0
    
    def test_find_by_date_range(self, repository, sample_order_data):
        """Тест поиска заказов по диапазону дат."""
        from datetime import datetime, timedelta
        
        base_date = datetime.now()
        
        # Создаём заказ с датой 5 дней назад
        order1 = repository.create(sample_order_data)
        order1.created_at = base_date - timedelta(days=5)
        repository.session.commit()
        
        # Создаём заказ с датой 2 дня назад
        order2 = repository.create(sample_order_data)
        order2.created_at = base_date - timedelta(days=2)
        repository.session.commit()
        
        # Создаём заказ с датой 1 день назад
        order3 = repository.create(sample_order_data)
        order3.created_at = base_date - timedelta(days=1)
        repository.session.commit()
        
        # Ищем заказы за последние 3 дня (включая сегодня)
        start_date = base_date - timedelta(days=3)
        end_date = base_date + timedelta(days=1)
        result = repository.find_by_date_range(start_date, end_date)
        
        found_ids = [o.id for o in result]
        assert order2.id in found_ids
        assert order3.id in found_ids
        assert order1.id not in found_ids
    
    def test_get_total_amount(self, repository, sample_order):
        """Тест подсчёта общей суммы заказа."""
        expected_total = 50000.0 + 3000.0 + 3000.0  # 56000
        total = repository.get_total_amount_for_order(sample_order.id)
        assert total == expected_total
    
    def test_get_total_amount_empty_order(self, repository):
        """Тест подсчёта суммы заказа без позиций."""
        order_data = {
            "customer_name": "Тест",
            "delivery_address": "Адрес",
            "status": "PENDING",
            "items": []
        }
        order = repository.create(order_data)
        total = repository.get_total_amount_for_order(order.id)
        assert total == 0.0
    
    def test_transaction_rollback_on_invalid_data(self, repository):
        """Тест транзакционности: откат при некорректных данных."""
        invalid_data = {
            "customer_name": "Тест",
            "delivery_address": "Адрес",
            "status": "PENDING",
            "items": [
                {"product_name": "Товар", "quantity": -1, "price": 100.0}
            ]
        }
        
        # Попытка создания должна вызвать ошибку
        with pytest.raises(Exception):
            repository.create(invalid_data)
        
        # Откатываем транзакцию вручную
        repository.session.rollback()
        
        # Проверяем, что заказ не был создан
        all_orders = repository.session.query(Order).filter(
            Order.customer_name == "Тест"
        ).all()
        assert len(all_orders) == 0
    
    def test_validate_status_constraint(self, repository, sample_order_data):
        """Тест проверки ограничений на статус."""
        invalid_data = {
            **sample_order_data,
            "status": "INVALID_STATUS"
        }
        
        with pytest.raises(Exception):
            repository.create(invalid_data)
        
        repository.session.rollback()
    
    def test_validate_quantity_constraint(self, repository, sample_order_data):
        """Тест проверки ограничений на количество."""
        invalid_data = {
            **sample_order_data,
            "items": [
                {"product_name": "Товар", "quantity": 0, "price": 100.0}
            ]
        }
        
        with pytest.raises(Exception):
            repository.create(invalid_data)
        
        repository.session.rollback()
    
    def test_calculate_delivery_cost_success(self, repository, sample_order, httpx_mock):
        """Тест успешного расчёта стоимости доставки."""
        expected_cost = 150.0
        httpx_mock.add_response(
            url="https://api.delivery.com/calculate",
            method="POST",
            json={"cost": expected_cost},
            status_code=200
        )
        
        cost = repository.calculate_delivery_cost(sample_order.id)
        
        assert cost == expected_cost
        
        # Проверяем запрос
        request = httpx_mock.get_request()
        assert request is not None
        assert str(request.url) == "https://api.delivery.com/calculate"
        
        # Используем request.content вместо request.json()
        request_data = json.loads(request.content)
        assert request_data["address"] == sample_order.delivery_address
        assert request_data["weight"] == 2.0
    
    def test_calculate_delivery_cost_server_error(self, repository, sample_order, httpx_mock):
        """Тест ошибки сервера при расчёте доставки."""
        httpx_mock.add_response(
            url="https://api.delivery.com/calculate",
            method="POST",
            status_code=500,
            text="Internal Server Error"
        )
        
        with pytest.raises(DeliveryCalculationException) as exc_info:
            repository.calculate_delivery_cost(sample_order.id)
        
        assert "Ошибка API доставки" in str(exc_info.value)
    
    def test_calculate_delivery_cost_connection_error(self, repository, sample_order, httpx_mock):
        """Тест ошибки соединения при расчёте доставки."""
        httpx_mock.add_exception(
            httpx.ConnectError("Connection refused")
        )
        
        with pytest.raises(DeliveryCalculationException) as exc_info:
            repository.calculate_delivery_cost(sample_order.id)
        
        assert "Ошибка соединения" in str(exc_info.value)
    
    def test_calculate_delivery_cost_invalid_response(self, repository, sample_order, httpx_mock):
        """Тест некорректного ответа от API доставки."""
        httpx_mock.add_response(
            url="https://api.delivery.com/calculate",
            method="POST",
            json={"error": "Invalid data"},
            status_code=200
        )
        
        with pytest.raises(DeliveryCalculationException) as exc_info:
            repository.calculate_delivery_cost(sample_order.id)
        
        assert "Некорректный ответ" in str(exc_info.value)
    
    def test_calculate_delivery_cost_order_not_found(self, repository):
        """Тест расчёта доставки для несуществующего заказа."""
        with pytest.raises(EntityNotFoundException) as exc_info:
            repository.calculate_delivery_cost(99999)
        
        assert "Order с ID 99999 не найден" in str(exc_info.value)