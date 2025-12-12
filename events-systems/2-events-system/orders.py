import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer


KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"
TOPIC = "new_orders"
GROUP_ID = "orders-service"

orders_storage: list[dict] = []


async def consume_orders(consumer: AIOKafkaConsumer):
    try:
        async for msg in consumer:
            order = json.loads(msg.value.decode("utf-8"))
            orders_storage.append(order)

            print(f"[ORDER CONSUMED] {order}")
    except asyncio.CancelledError:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="earliest",
    )

    await consumer.start()

    task = asyncio.create_task(consume_orders(consumer))

    app.state.kafka_consumer = consumer
    app.state.consumer_task = task

    yield

    task.cancel()
    await consumer.stop()


app = FastAPI(title="orders", lifespan=lifespan)


@app.get("/orders")
async def list_orders():
    return orders_storage
