"""
Модуль для управления пользователями в системе бронирования
"""

import re
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import secrets
import string


class User:
    """Класс пользователя"""

    def __init__(
        self,
        user_id: int,
        email: str,
        password: str,
        age: int,
        name: str,
        phone: Optional[str] = None,
        is_active: bool = True
    ):
        self.user_id = user_id
        self.email = email
        self.password = password
        self.age = age
        self.name = name
        self.phone = phone
        self.is_active = is_active
        self.created_at = datetime.now()


class UserValidator:
    """Валидатор пользователей"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Проверка email
        """
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Проверка пароля
        Требования:
        - Минимум 8 символов
        - Хотя бы одна цифра
        - Хотя бы одна заглавная буква
        - Хотя бы одна строчная буква
        """
        if not password:
            return False
        if len(password) < 8:
            return False
        has_digit = any(c.isdigit() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        return has_digit and has_upper and has_lower

    @staticmethod
    def validate_age(age: int) -> bool:
        """
        Проверка возраста
        Требования: 18-120 лет
        """
        if not isinstance(age, int):
            return False
        if age < 0:
            return False
        return 18 <= age <= 120

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Проверка телефона
        Формат: +7XXXXXXXXXX или 8XXXXXXXXXX
        """
        if not phone:
            return False
        pattern = r'^(\+7|8)\d{10}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Проверка имени
        Требования:
        - Не пустое
        - Только буквы, пробелы и дефисы
        - Не более 50 символов
        """
        if not name:
            return False
        if len(name) > 50:
            return False
        pattern = r'^[a-zA-Zа-яА-Я\s\-\.]+$'
        return bool(re.match(pattern, name))


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self):
        self._users: Dict[int, User] = {}
        self._validator = UserValidator()
        self._email_index: Dict[str, int] = {}

    def create_user(
        self,
        email: str,
        password: str,
        age: int,
        name: str,
        phone: Optional[str] = None
    ) -> User:
        """
        Создание пользователя
        """
        if not self._validator.validate_email(email):
            raise ValueError("Invalid email format")
        if not self._validator.validate_password(password):
            raise ValueError("Invalid password format")
        if not self._validator.validate_age(age):
            raise ValueError("Invalid age")
        if not self._validator.validate_name(name):
            raise ValueError("Invalid name")
        if phone and not self._validator.validate_phone(phone):
            raise ValueError("Invalid phone format")

        email_lower = email.lower()
        if email_lower in self._email_index:
            raise ValueError("Email already exists")

        user_id = len(self._users) + 1
        user = User(
            user_id=user_id,
            email=email,
            password=hashlib.sha256(password.encode()).hexdigest(),
            age=age,
            name=name,
            phone=phone
        )
        self._users[user_id] = user
        self._email_index[email_lower] = user_id
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Получение пользователя по email
        """
        email_lower = email.lower()
        user_id = self._email_index.get(email_lower)
        if user_id is not None:
            return self._users.get(user_id)
        return None

    def update_user(
        self,
        user_id: int,
        email: Optional[str] = None,
        age: Optional[int] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> User:
        """
        Обновление данных пользователя
        """
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User not found")

        if email:
            if not self._validator.validate_email(email):
                raise ValueError("Invalid email format")
            email_lower = email.lower()
            existing_user_id = self._email_index.get(email_lower)
            if existing_user_id is not None and existing_user_id != user_id:
                raise ValueError("Email already exists")
            old_email_lower = user.email.lower()
            if old_email_lower in self._email_index:
                del self._email_index[old_email_lower]
            user.email = email
            self._email_index[email_lower] = user_id

        if age is not None:
            if not self._validator.validate_age(age):
                raise ValueError("Invalid age")
            user.age = age

        if name:
            if not self._validator.validate_name(name):
                raise ValueError("Invalid name")
            user.name = name

        if phone is not None:
            if phone and not self._validator.validate_phone(phone):
                raise ValueError("Invalid phone format")
            user.phone = phone

        return user

    def delete_user(self, user_id: int) -> bool:
        """
        Удаление пользователя
        """
        if user_id in self._users:
            user = self._users[user_id]
            email_lower = user.email.lower()
            if email_lower in self._email_index:
                del self._email_index[email_lower]
            del self._users[user_id]
            return True
        return False

    def get_active_users(self) -> List[User]:
        """Получение активных пользователей"""
        return [u for u in self._users.values() if u.is_active]

    def search_users(self, query: str) -> List[User]:
        """
        Поиск пользователей
        """
        if not query:
            return []

        result = []
        query_lower = query.lower()
        for user in self._users.values():
            if query_lower in user.name.lower() or query_lower in user.email.lower():
                result.append(user)
        return result

    def generate_reset_token(self, email: str) -> str:
        """
        Генерация токена для сброса пароля
        """
        user = self.get_user_by_email(email)
        if not user:
            raise ValueError("User not found")

        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(32))
        return token