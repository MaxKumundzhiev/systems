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
    def __init__(self, rooms: List[Room]) -> None:
        self._rooms = rooms
        self._rooms_by_id: Dict[int, Room] = {room.id: room for room in rooms}

    async def find_all(self) -> List[Room]:
        return self._rooms.copy()

    async def find_by_id(self, room_id: int) -> Optional[Room]:
        return self._rooms_by_id.get(room_id)


class SearchRoomServiceImpl(SearchRoomService):
    def __init__(self, repo: RoomRepository) -> None:
        self._repo = repo

    async def find_rooms_by_request(self, request: SearchRequest) -> List[Room]:
        rooms: List[Room] = await self._repo.find_all()
        available: Optional[List[Room]] = []
        from_date, to_date = request.from_date, request.from_date + timedelta(
            days=request.days
        )

        for room in rooms:
            if self._check_price(request.budget, request.days, room.price):
                continue
            if self._check_capacity(request.guests, room.capacity):
                continue
            if self._check_amenities(request.amenities, room.amenities):
                continue
            if self._check_availability(from_date, to_date, room.bookings):
                continue
            available.append(room)
        return sorted(available, key=lambda room: room.id)

    async def _check_availability(
        self, requested_from: date, requested_to: date, bookings: List[Booking]
    ) -> bool:
        for booking in bookings:
            if not self._check_room_is_available(
                requested_from, requested_to, booking.from_date, booking.to_date
            ):
                return False
        return True

    async def _check_price(self, budget: int, days: int, price_per_day: int) -> bool:
        return price_per_day * days <= budget

    async def _check_capacity(self, guests: int, capacity: int) -> bool:
        return guests <= capacity

    async def _check_amenities(
        self, requested_amenities: Set[Amenity], available_amenties: Set[Amenity]
    ) -> bool:
        return requested_amenities.issubset(available_amenties)

    async def _check_room_is_available(
        self,
        requested_from: date,
        requested_to: date,
        available_from: date,
        available_to: date,
    ) -> bool:
        overlap = max(available_from, requested_from) < min(requested_to, available_to)
        return not overlap


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
            if not await self._search_room_service._check_availability(
                from_date, to_date, room.bookings
            ):
                raise ValueError(f"Room with id {room_id} is not available")

            room.bookings.append(booking)
            return booking
