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
    amenities: Set[Amenity]  # ✅ fixed name
    bookings: List[Booking]


@dataclass
class SearchRequest:
    from_date: date
    days: int
    guests: int
    budget: int
    amenities: Set[Amenity]  # ✅ fixed name


#### Interfaces ####
class RoomRepository(ABC):
    @abstractmethod
    async def find_all(self) -> List[Room]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, room_id: int) -> Optional[Room]:
        raise NotImplementedError


class SearchRoomService(ABC):
    @abstractmethod
    async def find_rooms_by_request(self, search_request: SearchRequest) -> List[Room]:
        raise NotImplementedError


#### Implementation ####
class SimpleRoomRepository(RoomRepository):
    """
    find_all() возвращает shallow copy списка: те же объекты Room.
    Изменения (например room.bookings.append в бронировании) видны везде — один объект в памяти.
    find_by_id использует Dict[int, Room] для O(1) доступа.
    """

    def __init__(self, rooms: List[Room]):
        self._rooms = rooms
        self._rooms_by_id: Dict[int, Room] = {r.id: r for r in rooms}

    async def find_all(self) -> List[Room]:
        return self._rooms.copy()

    async def find_by_id(self, room_id: int) -> Optional[Room]:
        return self._rooms_by_id.get(room_id)


class SearchRoomServiceImpl(SearchRoomService):
    def __init__(self, room_repository: RoomRepository):
        self.room_repository = room_repository

    async def find_rooms_by_request(self, request: SearchRequest) -> List[Room]:
        all_rooms = await self.room_repository.find_all()
        to_date = request.from_date + timedelta(days=request.days)

        available_rooms: List[Room] = []

        for room in all_rooms:
            if not self._check_price(room, request.budget, request.days):
                continue
            if not self._check_capacity(room, request.guests):
                continue
            if not self._check_amenities(room, request.amenities):
                continue
            if not self._check_availability(room, request.from_date, to_date):
                continue

            available_rooms.append(room)

        return sorted(available_rooms, key=lambda r: r.id)

    def _check_price(self, room: Room, budget: int, days: int) -> bool:
        return room.price * days <= budget

    def _check_capacity(self, room: Room, guests: int) -> bool:
        return room.capacity >= guests

    def _check_amenities(self, room: Room, required_amenities: Set[Amenity]) -> bool:
        return required_amenities.issubset(room.amenities)

    def _check_availability(self, room: Room, from_date: date, to_date: date) -> bool:
        return check_availability(room, from_date, to_date)


def check_availability(room: Room, from_date: date, to_date: date) -> bool:
    for booking in room.bookings:
        # overlap check
        if from_date < booking.to_date and to_date > booking.from_date:
            return False
    return True
