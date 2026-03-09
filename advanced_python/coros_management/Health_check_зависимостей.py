"""
Есть 3 async health-check-а:
    check_db()
    check_redis()
    check_s3()

Нужно параллельно выполнить все и вернуть:
    "ok", если все доступны
    список упавших зависимостей, если нет
"""

from collections.abc import Awaitable, Sequence
import asyncio


async def check_db() -> bool: ...
async def check_redis() -> bool: ...
async def check_s3() -> bool: ...


async def check_dependencies() -> str | list[str]:
    checks: dict[str, Awaitable[bool]] = {
        "db": check_db(),
        "redis": check_redis(),
        "s3": check_s3(),
    }

    results: Sequence[bool | BaseException] = await asyncio.gather(
        *checks.values(),
        return_exceptions=True,
    )

    failed: list[str] = []
    for name, result in zip(checks.keys(), results):
        if isinstance(result, BaseException) or result is False:
            failed.append(name)

    return "ok" if not failed else failed
