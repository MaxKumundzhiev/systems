"""
Для dashboard надо одновременно получить:
- пользователя
- заказы
- уведомления

Собери всё в один словарь.
"""

import asyncio
from typing import TypeVar, Awaitable

T = TypeVar("T")


async def get_user(user_id: str) -> dict: ...


async def get_orders(user_id: str) -> list[dict]: ...


async def get_notifications(user_id: str) -> list[dict]: ...


async def safe(coro: Awaitable[T]) -> T | None:
    try:
        return await coro
    except Exception:
        return None


async def build_dashboard(user_id: str) -> dict:
    user, orders, notifications = await asyncio.gather(
        safe(get_user(user_id)),
        safe(get_orders(user_id)),
        safe(get_notifications(user_id)),
        return_exceptions=True,
    )

    return {
        "user": user,
        "orders": orders or [],
        "notifications": notifications or [],
    }
