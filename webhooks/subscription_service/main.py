import datetime
import asyncio

from fastapi import FastAPI, status, responses
from pydantic import BaseModel

app = FastAPI(title="subscription service")


class SubscribeRequest(BaseModel):
    user_id: str
    tier_id: str


async def sse_event():
    while True:
        current_time = datetime.datetime.now().isoformat()
        message = f"data: Current time is {current_time}\n\n"
        yield message
        await asyncio.sleep(1)


@app.post(
    path="/subscribe",
    status_code=status.HTTP_202_ACCEPTED
)
async def subscribe(request: SubscribeRequest):
    return status.HTTP_202_ACCEPTED


@app.get(
    path="/events",
    status_code=status.HTTP_202_ACCEPTED
)
async def events():
    return responses.StreamingResponse(sse_event(), media_type="text/event-stream")