"""
Есть несколько независимых задач.
Нужно остановить ожидание, если хотя бы одна задача упала.

since we work with wait - it excpects Tasks for input
"""

import asyncio


async def job_1() -> str: ...


async def job_2() -> str: ...


async def job_3() -> str: ...


async def run_until_first_exception() -> tuple[set[asyncio.Task], set[asyncio.Task]]:
    tasks = {
        asyncio.create_task(job_1()),
        asyncio.create_task(job_2()),
        asyncio.create_task(job_3()),
    }

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    error = False
    for task in done:
        try:
            task.result()
        except Exception:
            error = True
            break

    if error:
        for task in pending:
            task.cancel()

    return done, pending


"""
import asyncio


async def job_1() -> str: ...
async def job_2() -> str: ...
async def job_3() -> str: ...


async def run_until_first_exception() -> tuple[set[asyncio.Task[str]], set[asyncio.Task[str]]]:
    tasks: set[asyncio.Task[str]] = {
        asyncio.create_task(job_1()),
        asyncio.create_task(job_2()),
        asyncio.create_task(job_3()),
    }

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    if any(task.exception() is not None for task in done):
        for task in pending:
            task.cancel()

    return done, pending
"""
