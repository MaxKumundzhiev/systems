"""
Есть:
- воркер чтения сообщений
- heartbeat
- отправка статистики

Если один падает — остальные тоже должны завершиться.
"""

import asyncio


async def read_messages() -> None: ...


async def heartbeat() -> None: ...


async def send_stats() -> None: ...


async def run_session_workers() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(read_messages())
            tg.create_task(heartbeat())
            tg.create_task(send_stats())
    except* Exception:
        raise
