"""
Есть шаги:
    - validate_order(order_id)
    - reserve_money(order_id)
    - mark_order_paid(order_id)
Все функции асинхронные.

Нужно написать process_payment(order_id), где шаги идут строго последовательно.
Если валидация не прошла — остальные шаги не выполняются.

Explanation
    в силу того что нам нужено соблюсти порядок и задачи должны быть выполнены последовательно
    мы можем использовать только await друг за другом
"""

from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class Order:
    id: str
    name: str


@dataclass
class OrderError:
    msg: str


async def validate_order(
    order_id: str,
) -> Tuple[Optional[Order], Optional[OrderError]]: ...
async def reserve_money(
    order_id: str,
) -> Tuple[Optional[Order], Optional[OrderError]]: ...
async def mark_order_paid(
    order_id: str,
) -> Tuple[Optional[Order], Optional[OrderError]]: ...


async def process_payment(order: Order) -> Optional[OrderError]:
    res, err = await validate_order(order.id)
    if err:
        return err

    res, err = await reserve_money(order.id)
    if err:
        return err

    res, err = await mark_order_paid(order.id)
    if err:
        return err

    return None
