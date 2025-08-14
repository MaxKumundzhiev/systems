from uuid import uuid4

from pydantic import BaseModel
from fastapi import FastAPI
from asyncio import Queue

app = FastAPI(title="Users Service")

QUEUE = Queue()


class SubscriptionReq(BaseModel):
    user_id: str
    callback_url: str
    secret: str


class AcceptedRes(BaseModel):
    request_id: str
    status: str = "ACCEPTED"


@app.post(path="/subscribe", response_model=AcceptedRes)
async def subscribe(req: SubscriptionReq):
    """
    1) кладём задачу на создание подписки
    2) мгновенно отвечаем 202 ACCEPTED
    """
    req_id = str(uuid4())
    event = {
        "kind": "NEW_SUBSCRIPTION",
        "request_id": req_id,
        "user_id": req.user_id,
        "callback_url": req.callback_url,
        "secret": req.secret
    }
    await QUEUE.put(event)
    return AcceptedRes(request_id=req_id)

