import asyncio
from contextlib import asynccontextmanager


class RWLock:
    def __init__(self) -> None:
        self._readers = 0
        self._writer = False
        self._writers_waiting = 0
        self._cond = asyncio.Condition()

    @asynccontextmanager
    async def read_lock(self):
        async with self._cond:
            while self._writer or self._writers_waiting > 0:
                await self._cond.wait()
            self._readers += 1

        try:
            yield
        finally:
            async with self._cond:
                self._readers -= 1
                if self._readers == 0:
                    self._cond.notify_all()

    @asynccontextmanager
    async def write_lock(self):
        async with self._cond:
            self._writers_waiting += 1
            try:
                while self._writer or self._readers > 0:
                    await self._cond.wait()
                self._writer = True
            finally:
                self._writers_waiting -= 1

        try:
            yield
        finally:
            async with self._cond:
                self._writer = False
                self._cond.notify_all()
