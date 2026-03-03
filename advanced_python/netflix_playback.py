"""
📌 Контекст
Пользователь нажимает Play. Запрос уходит на сервер: POST /play/{user_id}/{title_id}
Но сеть лагает. Клиент не получает ответ. Он автоматически ретраит тот же запрос 2–3 раза.

❌ Проблема без идемпотентности

Каждый запрос:
- создаёт новую playback session
- увеличивает счётчики аналитики
- может выдавать новую DRM-лицензию
- может считать устройство как новое активное

В итоге:
    3 одинаковых сессии
    испорченная аналитика
    нарушение лимитов устройств

🎯 Требование
Если клиент повторно отправляет тот же самый логический запрос,
сервер должен выполнить его ровно один раз. Повтор должен вернуть тот же результат, а не создать новый.

📦 Что даёт клиент
Каждый запрос содержит: client_request_id: str  # UUID

Пример:
{
  "user_id": 42,
  "title_id": 777,
  "client_request_id": "abc-123-uuid"
}
"""

import asyncio
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, AsyncIterator
from random import randint
from contextlib import asynccontextmanager


@dataclass(frozen=True)
class PlayRequest:
    user_id: int
    title_id: int
    client_request_id: str


@dataclass
class Session:
    id: int
    title_id: int
    user_id: int
    client_request_id: str


## Interfaces ##
class SessionsPlaybackRepository(ABC):
    @abstractmethod
    async def get_all_sessions(self) -> Dict[str, Session]:
        raise NotImplementedError

    @abstractmethod
    async def get_session_by_client_request_id(
        self, client_request_id: str
    ) -> Optional[Session]:
        raise NotImplementedError

    @abstractmethod
    async def insert_new_session(
        self, client_request_id: str, session: Session
    ) -> None:
        raise NotImplementedError


class SessionPlaybackService(ABC):
    @abstractmethod
    async def start_session(self, play_request: PlayRequest) -> Session:
        raise NotImplementedError


## Implementation ##
class SessionsLockManager:
    DEFAULT_POOL_SIZE: int = 512

    def __init__(self, pool_size: int = DEFAULT_POOL_SIZE):
        self._pool_size = pool_size
        self._locks: List[asyncio.Lock] = [asyncio.Lock() for _ in range(pool_size)]

    def _index(self, key: str) -> int:
        return hash(key) % self._pool_size

    @asynccontextmanager
    async def lock(self, client_request_id: str) -> AsyncIterator[None]:
        lock = self._locks[self._index(client_request_id)]
        async with lock:
            yield


class SimpleSessionsPlaybackRepository(SessionsPlaybackRepository):
    def __init__(self, sessions: Optional[List[Session]] = None) -> None:
        sessions = sessions or []
        self._sessions: Dict[str, Session] = {s.client_request_id: s for s in sessions}

    async def get_all_sessions(self) -> Dict[str, Session]:
        return self._sessions.copy()

    async def get_session_by_client_request_id(
        self, client_request_id: str
    ) -> Optional[Session]:
        return self._sessions.get(client_request_id)

    async def insert_new_session(
        self, client_request_id: str, session: Session
    ) -> None:
        self._sessions[client_request_id] = session


class SessionPlaybackServiceImpl(SessionPlaybackService):
    def __init__(
        self,
        repo: SessionsPlaybackRepository,
        sessions_lock_manager: SessionsLockManager,
    ) -> None:
        self._repo = repo
        self._locks_manager = sessions_lock_manager

    async def start_session(self, play_request: PlayRequest) -> Session:
        async with self._locks_manager.lock(play_request.client_request_id):
            session = await self._repo.get_session_by_client_request_id(
                play_request.client_request_id
            )
            if session is not None:
                return session

            new_session = Session(
                id=randint(0, 1_000_000),
                title_id=play_request.title_id,
                user_id=play_request.user_id,
                client_request_id=play_request.client_request_id,
            )
            await self._repo.insert_new_session(
                play_request.client_request_id, new_session
            )
            return new_session
