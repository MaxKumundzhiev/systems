"""
Есть fetch_exchange_rate(), который иногда зависает.
    Нужно ждать максимум 2 секунды:
        если успел — вернуть курс
        если нет — вернуть "temporary unavailable"
"""

import asyncio


async def fetch_exchange_rate() -> float: ...


async def get_rate() -> float | str:
    try:
        res = await asyncio.wait_for(fetch_exchange_rate(), timeout=2)
    # !!! fetch error with asyncio.TimeoutError
    except asyncio.TimeoutError:
        return "temporary unavailable"
    else:
        return res
