"""
Для одной сессии нужно одновременно получить:
    - профиль пользователя
    - историю попыток
    - подписку
    - настройки языка
"""

import asyncio
from collections.abc import Awaitable, Sequence


async def get_profile(user_id: str) -> dict: ...
async def get_subscription(user_id: str) -> dict: ...
async def get_language_settings(user_id: str) -> dict: ...
async def get_attempt_history(user_id: str) -> list[dict]: ...


async def build_session_context(user_id: str) -> dict[str, dict | list[dict] | None]:
    coros: dict[str, Awaitable[dict | list[dict]]] = {
        "profile": get_profile(user_id),
        "subscription": get_subscription(user_id),
        "language": get_language_settings(user_id),
        "history": get_attempt_history(user_id),
    }

    results: Sequence[dict | list[dict] | BaseException] = await asyncio.gather(
        *coros.values(),
        return_exceptions=True,
    )

    response: dict[str, dict | list[dict] | None] = {}

    for name, res in zip(coros.keys(), results):
        if isinstance(res, BaseException):
            response[name] = None
        else:
            response[name] = res

    return response


"""
async def build_session_context(user_id: str) -> dict[str, dict | list[dict]]:
    profile, subscription, language, history = await asyncio.gather(
        get_profile(user_id),
        get_subscription(user_id),
        get_language_settings(user_id),
        get_attempt_history(user_id),
    )

    return {
        "profile": profile,
        "subscription": subscription,
        "language": language,
        "history": history,
    }
"""
