"""
Нужно:
    - создать бронь в БД
    - после этого отправить письмо в фоне
    - API-ответ вернуть сразу после создания брони


Если не лочить (блокировки) - тогда будет проблема с гонкой за бронирование
На уровне одного инстанса лок окей, если кросс инстанс - тогда нужна блокировка на уровне базы
"""

import asyncio

from typing import Dict
from abc import ABC, abstractmethod
from datetime import date
from dataclasses import dataclass


@dataclass
class Booking:
    id: int
    room_id: int
    from_date: date
    to_date: date
    capacity: int
    budget: int


## Interfaces ##
class BookingRepository(ABC):
    @abstractmethod
    async def book_room(self, room_id: int) -> None:
        raise NotImplemented


class BookingService(ABC):
    @abstractmethod
    async def create_reservation(self, user_id: int, booking: Booking) -> None:
        raise NotImplemented


class EmailService(ABC):
    @abstractmethod
    async def send_confirmation_email(self, user_id: int, booking: Booking) -> None:
        raise NotImplemented


## Implementation ##
class SimpleBookingRepo(BookingRepository):
    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._rooms_by_id: Dict[int, bool] = {r: False for r in range(capacity)}

    async def book_room(self, room_id: int) -> None:
        if not self._rooms_by_id.get(room_id, False):
            self._rooms_by_id[room_id] = True
        else:
            raise Exception("room is already booked")


class BookingServiceImpl(BookingService):
    def __init__(self, repo: BookingRepository, email_ser: EmailService) -> None:
        self._repo = repo
        self._email_serv = email_ser

    async def create_reservation(self, user_id: int, booking: Booking) -> None:
        await self._repo.book_room(booking.room_id)
        asyncio.create_task(self._email_serv.send_confirmation_email(user_id, booking))
