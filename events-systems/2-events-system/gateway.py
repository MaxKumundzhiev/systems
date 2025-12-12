from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="gateway")


class OrderIn(BaseModel):
    name: str
    items: list[str]
    total_price: float


class OrderOut(BaseModel):
    id: str = str(uuid4())
    name: str
    items: list[str]
    total_price: float
    created_at: str = str(datetime.now())


class NewOrderNotification(BaseModel):
    event_name: str = "new_order_created"
    id: str
    created_at: str


@app.post("/orders/", response_model=OrderOut)
async def create_new_order(request: OrderIn):
    """
    write to kafka topic named new_orders
    """
    return OrderOut(**request.model_dump())


@app.post("/notifications/")
async def create_new_notification(request: NewOrderNotification):
    """
    write to kafka topic named new_orders
    """
    print(request)
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
