"""
Тебе нужно написать софт для небольшого отеля. Так как это MVP, то не будем использовать БД и сделаем все in-memory.

У бизнеса есть несколько требований к задаче:

Поиск свободных номеров. Реализация поиска свободных номеров по параметрам:
- Дата заезда
- Количество дней пребывания
- Количество человек
- Бюджет на поездку
- Удобства в комнате (wifi, ac, tv)

Какие рассуждения
Поидее у отеля есть база номеров - они либо свободны, либо заняты.
Более того, если они заняты, то на какой то период.

Это наводит на мысль, что для каждого номера нам нужно хранить даты, когда он занят
и в случае если пользователь хочет проверить на определенную дату то
1. мы должны найти подходящий номер по критериям (кроме даты)
2. проверить номер по датам

"""

from enum import StrEnum
from typing import Set, List, Optional, Dict
from datetime import date, timedelta
from dataclasses import dataclass

from abc import ABC, abstractmethod


@dataclass
class Booking:
    from_date: date
    to_date: date


class Amenity(StrEnum):
    wifi = "wifi"
    ac = "ac"
    tv = "tv"


@dataclass
class Room:
    id: int
    price: int
    capacity: int
    amenties: Set[Amenity]
    bookings: List[Booking]


@dataclass
class SearchRequest:
    from_date: date
    days: int
    guests: int
    budget: int
    amenties: Set[Amenity]


#### Interfaces ####
class RoomRepository(ABC):
    @abstractmethod
    async def find_all(self) -> List[Room]:
        pass

    @abstractmethod
    async def find_by_id(self, room_id: int) -> Optional[Room]:
        pass


class SearchRoomService(ABC):
    @abstractmethod
    async def find_rooms_by_request(self, search_request: SearchRequest) -> List[Room]:
        pass


#### Implementation ####
class SimpleRoomRepository(RoomRepository):
    def __init__(self, rooms: List[Room]) -> None:
        self._rooms = rooms
        self._rooms_by_id: Dict[int, Room] = {room.id: room for room in rooms}

    async def find_all(self) -> List[Room]:
        return self._rooms.copy()

    async def find_by_id(self, room_id: int) -> Optional[Room]:
        return self._rooms_by_id.get(room_id)


class SearchRoomServiceImpl(SearchRoomService):
    def __init__(self, repository: RoomRepository) -> None:
        self._repo = repository

    async def find_rooms_by_request(self, search_request: SearchRequest) -> List[Room]:
        # fetch all rooms from db
        rooms = await self._repo.find_all()

        date_from = search_request.from_date
        date_to = search_request.from_date + timedelta(days=search_request.days)

        # sequentially filter by: guests, budget, amnieties, finally dates
        available_rooms = []
        for room in rooms:
            if self._check_price(room, search_request.budget, search_request.days):
                continue

            if self._check_capacity(room, search_request.guests):
                continue

            if self._check_amnieties(room, search_request.amenties):
                continue

            if self._check_availability(room, date_from, date_to):
                continue

            available_rooms.append(room)

        return sorted(available_rooms, key=lambda r: r.id)

    async def _check_price(self, room: Room, budget: int, days: int) -> bool:
        return budget >= room.price * days

    async def _check_capacity(self, room: Room, guests: int) -> bool:
        return room.capacity >= guests

    async def _check_amnieties(self, room: Room, amnieties: Set[Amenity]) -> bool:
        return amnieties.issubset(room.amenties)

    async def _check_availability(
        self, room: Room, date_from: date, date_to: date
    ) -> bool:
        return await self._check_availability_for_all_bookings(
            room.bookings, date_from, date_to
        )

    async def _check_availability_for_all_bookings(
        self, bookings: List[Booking], date_from: date, date_to: date
    ) -> bool:
        """available if dates do not intersect (overlap)"""
        for booking in bookings:
            if date_from < booking.to_date and date_to > booking.from_date:
                return False
        return True
