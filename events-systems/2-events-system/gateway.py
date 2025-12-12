from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel, Field

from aiokafka import AIOKafkaProducer
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.kafka_producer = AIOKafkaProducer(bootstrap_servers="kafka:29092")
    await app.state.kafka_producer.start()
    yield
    await app.state.kafka_producer.stop()


app = FastAPI(title="gateway", lifespan=lifespan)


class OrderIn(BaseModel):
    name: str
    items: list[str]
    total_price: float


class OrderOut(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    items: list[str]
    total_price: float
    created_at: str = Field(default_factory=lambda: str(datetime.now()))


class NewOrderNotification(BaseModel):
    event_name: str = "new_order_created"
    id: str
    created_at: str


@app.post("/orders/", response_model=OrderOut)
async def create_new_order(request: OrderIn):
    """
    write to kafka topic named new_orders
    """
    topic: str = "new_orders"
    producer: AIOKafkaProducer = app.state.kafka_producer
    event = OrderOut(**request.model_dump())
    msg = event.model_dump_json().encode("utf-8")
    await producer.send_and_wait(topic, msg)
    print("message:" f"Message '{msg}' sent to Kafka topic '{topic}'")
    return event


@app.post("/notifications/")
async def create_new_notification(request: NewOrderNotification):
    """
    write to kafka topic named new_orders
    """
    topic: str = "notifications"
    producer: AIOKafkaProducer = app.state.kafka_producer
    msg = request.model_dump_json().encode("utf-8")
    await producer.send_and_wait(topic, msg)
    print("message:" f"Message '{msg}' sent to Kafka topic '{topic}'")
    return {"status": "sent notification"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
