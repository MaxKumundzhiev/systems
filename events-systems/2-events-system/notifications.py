import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer


KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"
TOPIC = "notifications"
GROUP_ID = "notifications-service"

notifications_storage: list[dict] = []


async def consume_notifications(consumer: AIOKafkaConsumer):
    try:
        async for msg in consumer:
            notification = json.loads(msg.value.decode("utf-8"))
            notifications_storage.append(notification)

            print(f"[NOTIFICATION CONSUMED] {notification}")
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

    task = asyncio.create_task(consume_notifications(consumer))

    app.state.kafka_consumer = consumer
    app.state.consumer_task = task

    yield

    task.cancel()
    await consumer.stop()


app = FastAPI(title="notifications", lifespan=lifespan)


@app.get("/notifications")
async def list_notifications():
    return notifications_storage
