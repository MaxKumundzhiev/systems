"""
asyncio.wait()

Есть два провайдера:
    - request_primary_provider()
    - request_backup_provider()

Нужно:
    - запустить оба запроса
    - дождаться первого завершившегося
    - взять первый успешный результат
    - вторую задачу отменить


asyncio.wait() gets set of Tasks or Futures objects,
meaning u need explicitly wrap coros into tasks, unlike asyncio.gather() does.

Маленький инсайт
В современном asyncio коде чаще используют:
    gather()        → wait all
    wait()          → stream results, low-level control
    as_completed()  → stream results
"""

import asyncio
from asyncio import Task


async def request_primary_provider() -> str: ...
async def request_backup_provider() -> str: ...


async def get_fastest_response() -> str:
    tasks: set[Task[str]] = {
        asyncio.create_task(request_primary_provider()),
        asyncio.create_task(request_backup_provider()),
    }

    done: set[Task[str]]
    pending: set[Task[str]]

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

    return next(iter(done)).result()
