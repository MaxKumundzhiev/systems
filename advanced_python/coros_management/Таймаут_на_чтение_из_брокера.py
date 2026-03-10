"""
Есть read_message()
    Нужно ждать сообщение максимум 1 секунду.
    Если сообщений нет — вернуть None.
"""

import asyncio


async def read_message() -> dict: ...


async def poll_once() -> dict | None:
    timeout = 1.0
    try:
        return await asyncio.wait_for(read_message(), timeout=timeout)
    except asyncio.TimeoutError:
        return None
