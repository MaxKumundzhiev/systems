"""
Есть список user_ids.
Нужно параллельно загрузить профили через fetch_profile(user_id) и вернуть все результаты.

asyncio.gather() - сохраняет результаты в порядке который передовался
внутри

async def gather(awaitables: List[Awaitable]):
    tasks = []
    awaitables = [None] * len(awaitables)

    for idx, aw in enumerate(awaitables):
        task = asyncio.create_task(aw)
        task.add_done_callback(
            lambda: t, i=idx: result.__setitem__(i, t.result())
        )
        tasks.append(task)
    await asyncio.wait(tasks)
    return results
"""

import asyncio
from typing import Awaitable
from collections.abc import Sequence


async def fetch_profile(user_id: int) -> dict: ...


async def fetch_profiles(user_ids: list[int]) -> list[dict]:
    coros: list[Awaitable[dict]] = [fetch_profile(user_id) for user_id in user_ids]

    results: Sequence[dict | BaseException] = await asyncio.gather(
        *coros,
        return_exceptions=True,
    )

    response: list[dict] = []
    for res in results:
        if isinstance(res, dict):
            response.append(res)

    return response
