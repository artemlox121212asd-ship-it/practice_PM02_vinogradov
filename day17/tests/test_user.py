# tests/test_user.py

import pytest
from src.user import User, UserValidator, UserService


class TestUserValidator:
    
    @pytest.fixture
    def validator(self):
        return UserValidator()
    
    # === Тесты для validate_email ===
    
    def test_validate_email_valid(self, validator):
        """Проверка валидного email"""
        assert validator.validate_email("test@example.com") is True
        assert validator.validate_email("user.name@domain.co.uk") is True
    
    def test_validate_email_invalid(self, validator):
        """Проверка невалидного email"""
        assert validator.validate_email("invalid") is False
        assert validator.validate_email("test@") is False
        assert validator.validate_email("@domain.com") is False
    
    @pytest.mark.parametrize("email, expected", [
        ("test@example.com", True),
        ("user@domain.ru", True),
        ("invalid", False),
        ("test@", False),
    ])
    def test_validate_email_parametrized(self, validator, email, expected):
        """Параметризованный тест email"""
        assert validator.validate_email(email) is expected
    
    # === Тесты для validate_password ===
    
    def test_validate_password_valid(self, validator):
        """Проверка валидного пароля"""
        assert validator.validate_password("Password123") is True
        assert validator.validate_password("StrongP@ssword1") is True
    
    def test_validate_password_invalid(self, validator):
        """Проверка невалидного пароля"""
        assert validator.validate_password("") is False
        assert validator.validate_password("password") is False  # нет заглавной
        assert validator.validate_password("PASSWORD") is False  # нет цифры
        assert validator.validate_password("Pass123") is False  # нет спецсимвола
    
    # === Тесты для validate_age ===
    
    def test_validate_age_valid(self, validator):
        """Проверка валидного возраста"""
        assert validator.validate_age(25) is True
        assert validator.validate_age(18) is True
    
    def test_validate_age_invalid(self, validator):
        """Проверка невалидного возраста"""
        assert validator.validate_age(17) is False
        assert validator.validate_age(150) is False
    
    # === Тесты для validate_phone ===
    
    def test_validate_phone_valid(self, validator):
        """Проверка валидного телефона"""
        assert validator.validate_phone("+71234567890") is True
    
    def test_validate_phone_invalid(self, validator):
        """Проверка невалидного телефона"""
        assert validator.validate_phone("") is False
        assert validator.validate_phone("123") is False
    
    # === Тесты для validate_name ===
    
    def test_validate_name_valid(self, validator):
        """Проверка валидного имени"""
        assert validator.validate_name("John Doe") is True
        assert validator.validate_name("Anna-Marie") is True
    
    def test_validate_name_invalid(self, validator):
        """Проверка невалидного имени"""
        assert validator.validate_name("") is False
        assert validator.validate_name("John123") is False
        assert validator.validate_name("A" * 51) is False


class TestUserService:
    
    @pytest.fixture
    def service(self):
        return UserService()
    
    # === Тесты для create_user ===
    
    def test_create_user_valid(self, service):
        """Создание валидного пользователя"""
        user = service.create_user(
            email="test@example.com",
            password="Password123",
            age=25,
            name="John Doe"
        )
        assert user.user_id == 1
        assert user.email == "test@example.com"
        assert user.age == 25
        assert user.name == "John Doe"
    
    def test_create_user_invalid_email(self, service):
        """Создание с невалидным email"""
        with pytest.raises(ValueError, match="Invalid email format"):
            service.create_user(
                email="invalid",
                password="Password123",
                age=25,
                name="John Doe"
            )
    
    def test_create_user_invalid_password(self, service):
        """Создание с невалидным паролем"""
        with pytest.raises(ValueError, match="Invalid password format"):
            service.create_user(
                email="test@example.com",
                password="weak",
                age=25,
                name="John Doe"
            )
    
    # === Тесты для get_user ===
    
    def test_get_user_exists(self, service):
        """Получение существующего пользователя"""
        created = service.create_user(
            email="test@example.com",
            password="Password123",
            age=25,
            name="John Doe"
        )
        user = service.get_user(created.user_id)
        assert user is not None
        assert user.user_id == created.user_id
    
    def test_get_user_not_exists(self, service):
        """Получение несуществующего пользователя"""
        user = service.get_user(999)
        assert user is None
    
    # === Тесты для get_user_by_email ===
    
    def test_get_user_by_email_exists(self, service):
        """Поиск по существующему email"""
        service.create_user(
            email="test@example.com",
            password="Password123",
            age=25,
            name="John Doe"
        )
        user = service.get_user_by_email("test@example.com")
        assert user is not None
        assert user.email == "test@example.com"
    
    def test_get_user_by_email_not_exists(self, service):
        """Поиск по несуществующему email"""
        user = service.get_user_by_email("nonexistent@example.com")
        assert user is None
    
    # === Тесты для update_user ===
    
    def test_update_user_valid(self, service):
        """Обновление данных пользователя"""
        created = service.create_user(
            email="test@example.com",
            password="Password123",
            age=25,
            name="John Doe"
        )
        updated = service.update_user(
            created.user_id,
            email="new@example.com",
            age=30,
            name="Jane Doe"
        )
        assert updated.email == "new@example.com"
        assert updated.age == 30
        assert updated.name == "Jane Doe"
    
    def test_update_user_not_exists(self, service):
        """Обновление несуществующего пользователя"""
        with pytest.raises(ValueError, match="User not found"):
            service.update_user(999, email="new@example.com")
    
    # === Тесты для delete_user ===
    
    def test_delete_user_exists(self, service):
        """Удаление существующего пользователя"""
        created = service.create_user(
            email="test@example.com",
            password="Password123",
            age=25,
            name="John Doe"
        )
        result = service.delete_user(created.user_id)
        assert result is True
        assert service.get_user(created.user_id) is None
    
    def test_delete_user_not_exists(self, service):
        """Удаление несуществующего пользователя"""
        result = service.delete_user(999)
        assert result is False
    
    # === Тесты для search_users ===
    
    def test_search_users(self, service):
        """Поиск пользователей"""
        service.create_user(
            email="john@example.com",
            password="Password123",
            age=25,
            name="John Doe"
        )
        service.create_user(
            email="jane@example.com",
            password="Password123",
            age=30,
            name="Jane Smith"
        )
        results = service.search_users("john")
        assert len(results) == 1
        assert results[0].name == "John Doe"
    
    def test_search_users_empty(self, service):
        """Поиск по пустому запросу"""
        results = service.search_users("")
        assert len(results) == 0