"""
await coro()

Есть async-функция get_user(user_id), которая читает пользователя из БД.
Нужно написать handle_request(user_id), которая:
    - получает пользователя
    - если он не найден — возвращает "not found"
    - если найден — возвращает его email
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class User:
    user_id: int
    email: str


# interfaces
class UserRepository(ABC):
    @abstractmethod
    async def get_user(self, user_id: int) -> Optional[User]:
        raise NotImplemented


class UserService(ABC):
    @abstractmethod
    async def handle_request(self, user_id: int) -> str:
        raise NotImplemented


# implementation
class SimpleUserRepository(UserRepository):
    def __init__(self, users: List[User] | None = None) -> None:
        self._users: List[User] = users or []
        self._users_by_id: Dict[int, User] = {u.user_id: u for u in self._users}

    async def get_user(self, user_id: int) -> Optional[User]:
        return self._users_by_id.get(user_id)


class UserServiceImpl(UserService):
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def handle_request(self, user_id: int) -> str:
        user = await self._repo.get_user(user_id)
        if not user:
            return "Not found"
        return user.email
