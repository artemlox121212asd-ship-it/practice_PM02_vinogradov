# tests/test_user_full.py

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
        assert validator.validate_email("user+tag@domain.com") is True

    def test_validate_email_invalid(self, validator):
        """Проверка невалидного email"""
        assert validator.validate_email("") is False
        assert validator.validate_email("invalid") is False
        assert validator.validate_email("test@") is False
        assert validator.validate_email("@domain.com") is False
        assert validator.validate_email("test@domain") is False

    @pytest.mark.parametrize("email, expected", [
        ("test@example.com", True),
        ("user@domain.ru", True),
        ("invalid", False),
        ("test@", False),
        ("", False),
        ("test@domain", False),
    ])
    def test_validate_email_parametrized(self, validator, email, expected):
        """Параметризованный тест email"""
        assert validator.validate_email(email) is expected

    # === Тесты для validate_password ===

    def test_validate_password_valid(self, validator):
        """Проверка валидного пароля"""
        assert validator.validate_password("Password123") is True
        assert validator.validate_password("StrongP@ssword1") is True
        assert validator.validate_password("A1b2C3d4!") is True

    def test_validate_password_invalid(self, validator):
        """Проверка невалидного пароля"""
        assert validator.validate_password("") is False
        assert validator.validate_password("short") is False
        assert validator.validate_password("password") is False
        assert validator.validate_password("PASSWORD") is False
        assert validator.validate_password("Pass123") is False  # 7 символов
        assert validator.validate_password("Pass1!") is False   # 6 символов

    @pytest.mark.parametrize("password, expected", [
        ("Password123!", True),
        ("A1b2C3d4$", True),
        ("P@ssw0rd", True),
        ("", False),
        ("short", False),
        ("password", False),
        ("PASSWORD123", False),
        ("Pass123", False),   # 7 символов
        ("Pass1!", False),    # 6 символов
    ])
    def test_validate_password_parametrized(self, validator, password, expected):
        """Параметризованный тест пароля"""
        assert validator.validate_password(password) is expected

    # === Тесты для validate_age ===

    def test_validate_age_valid(self, validator):
        """Проверка валидного возраста"""
        assert validator.validate_age(18) is True
        assert validator.validate_age(25) is True
        assert validator.validate_age(120) is True

    def test_validate_age_invalid(self, validator):
        """Проверка невалидного возраста"""
        assert validator.validate_age(17) is False
        assert validator.validate_age(121) is False
        assert validator.validate_age(-1) is False
        assert validator.validate_age(0) is False

    @pytest.mark.parametrize("age, expected", [
        (18, True),
        (25, True),
        (120, True),
        (17, False),
        (121, False),
        (-1, False),
        (0, False),
    ])
    def test_validate_age_parametrized(self, validator, age, expected):
        """Параметризованный тест возраста"""
        assert validator.validate_age(age) is expected

    # === Тесты для validate_phone ===

    def test_validate_phone_valid(self, validator):
        """Проверка валидного телефона"""
        assert validator.validate_phone("+71234567890") is True
        assert validator.validate_phone("81234567890") is True

    def test_validate_phone_invalid(self, validator):
        """Проверка невалидного телефона"""
        assert validator.validate_phone("") is False
        assert validator.validate_phone("123") is False
        assert validator.validate_phone("+7123456789") is False
        assert validator.validate_phone("71234567890") is False
        assert validator.validate_phone("+712345678901") is False

    # === Тесты для validate_name ===

    def test_validate_name_valid(self, validator):
        """Проверка валидного имени"""
        assert validator.validate_name("John Doe") is True
        assert validator.validate_name("Anna-Marie") is True
        assert validator.validate_name("Иван Иванов") is True

    def test_validate_name_invalid(self, validator):
        """Проверка невалидного имени"""
        assert validator.validate_name("") is False
        assert validator.validate_name("John123") is False
        assert validator.validate_name("John@Doe") is False
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
            password="Password123!",
            age=25,
            name="John Doe"
        )
        assert user.user_id == 1
        assert user.email == "test@example.com"
        assert user.age == 25
        assert user.name == "John Doe"
        assert user.is_active is True

    def test_create_user_duplicate_email(self, service):
        """Создание пользователя с дублирующимся email"""
        service.create_user(
            email="test@example.com",
            password="Password123!",
            age=25,
            name="John Doe"
        )
        with pytest.raises(ValueError, match="Email already exists"):
            service.create_user(
                email="test@example.com",
                password="Password123!",
                age=30,
                name="Jane Doe"
            )

    def test_create_user_invalid_email(self, service):
        """Создание с невалидным email"""
        with pytest.raises(ValueError, match="Invalid email format"):
            service.create_user(
                email="invalid",
                password="Password123!",
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

    def test_create_user_invalid_age(self, service):
        """Создание с невалидным возрастом"""
        with pytest.raises(ValueError, match="Invalid age"):
            service.create_user(
                email="test@example.com",
                password="Password123!",
                age=17,
                name="John Doe"
            )

    def test_create_user_invalid_name(self, service):
        """Создание с невалидным именем"""
        with pytest.raises(ValueError, match="Invalid name"):
            service.create_user(
                email="test@example.com",
                password="Password123!",
                age=25,
                name=""
            )

    # === Тесты для get_user ===

    def test_get_user_exists(self, service):
        """Получение существующего пользователя"""
        created = service.create_user(
            email="test@example.com",
            password="Password123!",
            age=25,
            name="John Doe"
        )
        user = service.get_user(created.user_id)
        assert user is not None
        assert user.user_id == created.user_id
        assert user.email == created.email

    def test_get_user_not_exists(self, service):
        """Получение несуществующего пользователя"""
        user = service.get_user(999)
        assert user is None

    # === Тесты для get_user_by_email ===

    def test_get_user_by_email_exists(self, service):
        """Поиск по существующему email"""
        service.create_user(
            email="test@example.com",
            password="Password123!",
            age=25,
            name="John Doe"
        )
        user = service.get_user_by_email("test@example.com")
        assert user is not None
        assert user.email == "test@example.com"

    def test_get_user_by_email_case_insensitive(self, service):
        """Поиск по email без учета регистра"""
        service.create_user(
            email="test@example.com",
            password="Password123!",
            age=25,
            name="John Doe"
        )
        user = service.get_user_by_email("TEST@example.com")
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
            password="Password123!",
            age=25,
            name="John Doe"
        )
        updated = service.update_user(
            created.user_id,
            email="new@example.com",
            age=30,
            name="Jane Doe",
            phone="+71234567890"
        )
        assert updated.email == "new@example.com"
        assert updated.age == 30
        assert updated.name == "Jane Doe"
        assert updated.phone == "+71234567890"

    def test_update_user_partial(self, service):
        """Частичное обновление данных"""
        created = service.create_user(
            email="test@example.com",
            password="Password123!",
            age=25,
            name="John Doe"
        )
        updated = service.update_user(
            created.user_id,
            age=30
        )
        assert updated.email == "test@example.com"
        assert updated.age == 30
        assert updated.name == "John Doe"

    def test_update_user_duplicate_email(self, service):
        """Обновление на существующий email"""
        service.create_user(
            email="user1@example.com",
            password="Password123!",
            age=25,
            name="User One"
        )
        user2 = service.create_user(
            email="user2@example.com",
            password="Password123!",
            age=30,
            name="User Two"
        )
        with pytest.raises(ValueError, match="Email already exists"):
            service.update_user(
                user2.user_id,
                email="user1@example.com"
            )

    def test_update_user_not_exists(self, service):
        """Обновление несуществующего пользователя"""
        with pytest.raises(ValueError, match="User not found"):
            service.update_user(999, email="new@example.com")

    # === Тесты для delete_user ===

    def test_delete_user_exists(self, service):
        """Удаление существующего пользователя"""
        created = service.create_user(
            email="test@example.com",
            password="Password123!",
            age=25,
            name="John Doe"
        )
        result = service.delete_user(created.user_id)
        assert result is True
        assert service.get_user(created.user_id) is None
        assert service.get_user_by_email("test@example.com") is None

    def test_delete_user_not_exists(self, service):
        """Удаление несуществующего пользователя"""
        result = service.delete_user(999)
        assert result is False

    # === Тесты для get_active_users ===

    def test_get_active_users(self, service):
        """Получение активных пользователей"""
        user1 = service.create_user(
            email="user1@example.com",
            password="Password123!",
            age=25,
            name="User One"
        )
        user2 = service.create_user(
            email="user2@example.com",
            password="Password123!",
            age=30,
            name="User Two"
        )
        user2.is_active = False

        active = service.get_active_users()
        assert len(active) == 1
        assert active[0].user_id == user1.user_id

    # === Тесты для search_users ===

    def test_search_users(self, service):
        """Поиск пользователей"""
        service.create_user(
            email="john@example.com",
            password="Password123!",
            age=25,
            name="John Doe"
        )
        service.create_user(
            email="jane@example.com",
            password="Password123!",
            age=30,
            name="Jane Smith"
        )
        results = service.search_users("john")
        assert len(results) == 1
        assert results[0].name == "John Doe"

    def test_search_users_by_email(self, service):
        """Поиск по email"""
        service.create_user(
            email="john@example.com",
            password="Password123!",
            age=25,
            name="John Doe"
        )
        results = service.search_users("john@")
        assert len(results) == 1
        assert results[0].email == "john@example.com"

    def test_search_users_empty_query(self, service):
        """Поиск по пустому запросу"""
        service.create_user(
            email="test@example.com",
            password="Password123!",
            age=25,
            name="John Doe"
        )
        results = service.search_users("")
        assert len(results) == 0

    def test_search_users_not_found(self, service):
        """Поиск несуществующего пользователя"""
        service.create_user(
            email="test@example.com",
            password="Password123!",
            age=25,
            name="John Doe"
        )
        results = service.search_users("nonexistent")
        assert len(results) == 0

    # === Тесты для generate_reset_token ===

    def test_generate_reset_token_valid(self, service):
        """Генерация токена для существующего пользователя"""
        service.create_user(
            email="test@example.com",
            password="Password123!",
            age=25,
            name="John Doe"
        )
        token = service.generate_reset_token("test@example.com")
        assert token is not None
        assert len(token) == 32

    def test_generate_reset_token_invalid_email(self, service):
        """Генерация токена для несуществующего пользователя"""
        with pytest.raises(ValueError, match="User not found"):
            service.generate_reset_token("nonexistent@example.com")