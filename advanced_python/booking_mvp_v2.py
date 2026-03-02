import asyncio

from dataclasses import dataclass
from datetime import date, timedelta

from enum import StrEnum
from typing import List, Set, Dict, Optional, AsyncIterator

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager


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
    amenities: Set[Amenity]
    bookings: List[Booking]


@dataclass
class SearchRequest:
    from_date: date
    days: int
    guests: int
    budget: int
    amenities: Set[Amenity]


### Interfaces ###
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


class BookService(ABC):
    @abstractmethod
    async def book_room(self, room_id: int, from_date: date, days: int) -> Booking:
        pass


### Implementation ###
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


class LockPoolManager:
    """
    use list where idx gonna be hash(room_id) % pool_size and value gonna be a Lock as asyncmanager
    meaning we gonna yield a lock

    API
        def _index(room_id: int) -> int
        async def lock_room(room_id: int) -> AsyncIterator[None] <- here we encapsualte locking a resourse
    """

    DEFAULT_POOL_SIZE: int = 512

    def __init__(self, pool_size: int = DEFAULT_POOL_SIZE) -> None:
        self._pool_size = pool_size
        self._locks: List[asyncio.Lock] = [asyncio.Lock() for _ in range(pool_size)]

    def _index(self, room_id: int) -> int:
        return hash(room_id) % self._pool_size

    @asynccontextmanager
    async def lock_room(self, room_id: int) -> AsyncIterator[None]:
        idx = self._index(room_id)
        lock = self._locks[idx]

        async with lock:
            yield


class BookServiceImpl(BookService):
    def __init__(
        self,
        repo: RoomRepository,
        search_room_service: SearchRoomService,
        lock_pool_manager: LockPoolManager,
    ) -> None:
        self._repo = repo
        self._search_room_service = search_room_service
        self._lock_pool_manager = lock_pool_manager

    async def book_room(self, room_id: int, from_date: date, days: int) -> Booking:
        to_date: date = from_date + timedelta(days=days)
        booking = Booking(from_date, to_date)

        if days <= 0:
            raise ValueError("Days must be grater 0")
        if from_date < date.today():
            raise ValueError("From date should be from today or future (not past)")

        async with self._lock_pool_manager.lock_room(room_id):
            room: Optional[Room] = await self._repo.find_by_id(room_id)
            if not room:
                raise ValueError(f"Room with id {room_id} is not found")
            if not check_availability(room, from_date, to_date):
                raise ValueError(
                    f"Room with id {room_id} is not available for period from {from_date} to {to_date}"
                )

            room.bookings.append(booking)
            return booking
