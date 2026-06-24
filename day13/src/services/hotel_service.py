# src/services/hotel_service.py

from typing import List, Optional
from src.domain.models import Hotel
from src.domain.exceptions import HotelNotFoundError
from src.dto.hotel_dto import HotelCreateDTO, HotelResponseDTO, HotelUpdateDTO
from src.uow.unit_of_work import UnitOfWork


class HotelService:
    """Сервис для управления отелями."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.hotel_repo = uow.hotels

    def create(self, dto: HotelCreateDTO) -> HotelResponseDTO:
        """Создать новый отель."""
        hotel = Hotel(
            id=None,
            name=dto.name,
            address=dto.address,
            phone=dto.phone,
            rating=dto.rating or 0.0
        )
        saved = self.hotel_repo.add(hotel)
        self.uow.commit()
        return HotelResponseDTO.model_validate(saved)

    def get_by_id(self, hotel_id: int) -> HotelResponseDTO:
        """Получить отель по ID."""
        hotel = self.hotel_repo.get_by_id(hotel_id)
        if not hotel:
            raise HotelNotFoundError(f"Отель {hotel_id} не найден")
        return HotelResponseDTO.model_validate(hotel)

    def get_all(self, **filters) -> List[HotelResponseDTO]:
        """Получить все отели с фильтрацией."""
        hotels = self.hotel_repo.get_all(**filters)
        return [HotelResponseDTO.model_validate(h) for h in hotels]

    def update(self, hotel_id: int, dto: HotelUpdateDTO) -> HotelResponseDTO:
        """Обновить данные отеля."""
        hotel = self.hotel_repo.get_by_id(hotel_id)
        if not hotel:
            raise HotelNotFoundError(f"Отель {hotel_id} не найден")

        if dto.name is not None:
            hotel.name = dto.name
        if dto.address is not None:
            hotel.address = dto.address
        if dto.phone is not None:
            hotel.phone = dto.phone
        if dto.rating is not None:
            hotel.rating = dto.rating

        updated = self.hotel_repo.update(hotel)
        self.uow.commit()
        return HotelResponseDTO.model_validate(updated)

    def delete(self, hotel_id: int) -> bool:
        """Удалить отель."""
        hotel = self.hotel_repo.get_by_id(hotel_id)
        if not hotel:
            raise HotelNotFoundError(f"Отель {hotel_id} не найден")
        result = self.hotel_repo.delete(hotel_id)
        self.uow.commit()
        return result