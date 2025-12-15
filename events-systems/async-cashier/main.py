from datetime import datetime
from random import random, randint
from asyncio import Queue, sleep, create_task
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

to_process_orders: Queue[dict[str, Any]] = Queue()
success_orders: Queue[dict[str, Any]] = Queue()
failed_orders: Queue[dict[str, Any]] = Queue()


async def process_tasks(worker_id: int = 1):
    while True:
        order = await to_process_orders.get()  # ждём новый заказ
        try:
            to_sleep = randint(0, 5)
            rnd = random()
            await sleep(to_sleep)

            if rnd > 0.5:
                await success_orders.put(order)
            else:
                await failed_orders.put(order)
        finally:
            to_process_orders.task_done()


@app.on_event("startup")
async def startup():
    # один (или несколько) воркеров
    app.state.worker = [create_task(process_tasks(worker_id=id)) for id in range(8)]
    # если хочешь параллельнее:
    # app.state.workers = [create_task(process_tasks(i)) for i in range(1, 4)]


class Order(BaseModel):
    total_price: float
    order_time: datetime = Field(default_factory=datetime.now)


@app.post("/orders")
async def create_order(request: Order) -> dict:
    order = request.model_dump()
    await to_process_orders.put(order)
    return {"status": "added"}


def _queue_snapshot(q: Queue) -> list[dict[str, Any]]:
    # ВНИМАНИЕ: это "снимок" без await: просто читаем текущее содержимое
    return list(q._queue)  # type: ignore[attr-defined]


@app.get("/orders")
async def list_orders():
    waiting = _queue_snapshot(to_process_orders)
    successful = _queue_snapshot(success_orders)
    failed = _queue_snapshot(failed_orders)

    return {
        "counts": {
            "waiting": len(waiting),
            "successful": len(successful),
            "failed": len(failed),
        },
        "waiting": waiting,
        "successful": successful,
        "failed": failed,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
