# Спецификация сервиса валидации бронирований в гостинице

## 1. Назначение
Сервис проверяет корректность бронирования номера в гостинице и вычисляет риск мошенничества или отмены.

## 2. Входной формат

### JSON Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "user_id",
    "created_at",
    "booking_date",
    "check_in",
    "check_out",
    "guests",
    "children",
    "child_seat",
    "total_amount",
    "passport_country",
    "card_country"
  ],
  "properties": {
    "user_id": {
      "type": "integer",
      "description": "ID пользователя в системе",
      "minimum": 1
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Дата и время регистрации пользователя"
    },
    "booking_date": {
      "type": "string",
      "format": "date-time",
      "description": "Дата и время оформления бронирования"
    },
    "check_in": {
      "type": "string",
      "format": "date",
      "description": "Дата заезда"
    },
    "check_out": {
      "type": "string",
      "format": "date",
      "description": "Дата выезда"
    },
    "guests": {
      "type": "integer",
      "description": "Количество гостей",
      "minimum": 1,
      "maximum": 10
    },
    "children": {
      "type": "integer",
      "description": "Количество детей",
      "minimum": 0
    },
    "child_seat": {
      "type": "boolean",
      "description": "Флаг необходимости детского кресла",
      "default": false
    },
    "total_amount": {
      "type": "number",
      "description": "Общая стоимость бронирования",
      "minimum": 0,
      "maximum": 1000000
    },
    "phone_changed_at": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "Дата и время последней смены телефона"
    },
    "passport_country": {
      "type": "string",
      "description": "Страна паспорта (ISO-код)",
      "minLength": 2,
      "maxLength": 2
    },
    "card_country": {
      "type": "string",
      "description": "Страна платежной карты (ISO-код)",
      "minLength": 2,
      "maxLength": 2
    }
  }
}