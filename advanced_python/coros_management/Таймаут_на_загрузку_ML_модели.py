"""
Во время старта сервиса вызывается load_model().
Если модель грузится дольше 10 секунд, сервис должен упасть с ошибкой.
"""

import asyncio


class ModelStartupError(Exception):
    pass


async def load_model() -> object: ...


async def cleanup(task: asyncio.Task) -> None:
    if not task.done():
        task.cancel()
    await asyncio.gather(task, return_exceptions=True)


async def startup() -> object:
    task: asyncio.Task[object] = asyncio.create_task(load_model())
    try:
        return await asyncio.wait_for(task, timeout=10.0)
    except asyncio.TimeoutError:
        await cleanup(task)
        raise ModelStartupError
    except Exception:
        await cleanup(task)
        raise
