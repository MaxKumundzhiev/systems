"""
Представим что мы разрабатываем систему бронирования для отеля, в котором 10_000 комнат.

Нам нужно решение, которое позволяет конкурентно бронировать комнаты.
Что мы можем здесь:
1. Использовать lock на весь отель, это решит проблемы, но бронирование станет последовательным. А мы хотим крнкурентности.
2. Использовать lock на все комнаты отеля, это решит проблему последовательности, но будет неэффективно. При масштабирование упремся в ограничение ресурсов машины.
3. Использовать lock manager с predefined количество локов (lock pool) - которое будет меньше, чем комнат.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI


class PoolLockManager:
    DEFAULT_POOL_SIZE = 512

    def __init__(self, pool_size: int = DEFAULT_POOL_SIZE) -> None:
        # 1. Создаем массив из 512 блоков
        self._locks = [asyncio.Lock() for _ in range(pool_size)]
        self._pool_size = pool_size

    def _index(self, room_id: int) -> int:
        # 2. Магия математики (Modulo)
        # Мы вычисляем, какой из 512 блоков отвечает за эту комнату.
        # Room 1 -> index 1
        # Room 513 -> index 1 (так как 513 % 512 == 1)
        return hash(room_id) % self._pool_size

    @asynccontextmanager
    async def get_lock(self, room_id: int):
        # 3. Берем нужный блок и отдаем его
        idx = self._index(room_id)
        lock = self._locks[idx]

        async with lock:
            yield  # <-- Тут используем обычный asyncio.Lock


pool_lock_manager = PoolLockManager()
rooms = {key: False for (key, _) in enumerate(range(1_000_000))}

app = FastAPI()


@app.post("/book/{room_id}")
async def book_room(room_id: int):
    async with pool_lock_manager.get_lock(room_id):
        # Симулируем долгую операцию
        await asyncio.sleep(0.5)

        if rooms[room_id]:
            return {"room_id": room_id, "status": "already_booked"}

        rooms[room_id] = True
        return {"room_id": room_id, "status": "booked"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
