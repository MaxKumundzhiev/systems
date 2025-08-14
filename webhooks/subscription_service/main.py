import time
import asyncio
from uuid import uuid4
from typing import Dict

import redis

from fastapi import FastAPI, status, HTTPException
from fastapi.responses import StreamingResponse

from pydantic import BaseModel


app = FastAPI(title="subscription service")
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

STREAM = "events:subscriptions"

class SubscribeRequest(BaseModel):
    user_id: str
    tier_id: str


def generate_new_subscription_event(
        user_id: str, tier_id: str, req_id: str
    ) -> Dict:
    now = int(time.time())
    return {
        "req_id": req_id,
        "user_id": user_id,
        "tier_id": tier_id,
        "status": "PENDING",
        "event": "NEW_SUBSCRIPTION",
        "created_at": str(now),
        "updated_at": str(now),
        "ver": "1",
        "last_req_id": req_id
    }

@app.post(
    path="/subscribe",
    status_code=status.HTTP_202_ACCEPTED
)
async def subscribe(request: SubscribeRequest):
    user_id, tier_id, req_id = request.user_id, request.tier_id, str(uuid4())
    sub_key = f"subscription:{user_id}"

    # check current state in stream (if event with such req_id exists)
    cur_event = r.hget(name=sub_key, key="event")
    if cur_event in {"CREATED_SUBSCRIPTION", "ACTIVE_SUBSCRIPTION"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already subscribed")
    
    # generate new event
    event = generate_new_subscription_event(user_id=user_id, tier_id=tier_id, req_id=req_id)
    try:
        # write event to the queue
        r.xadd(STREAM, event, maxlen=1_000_000, approximate=True)
        # write event to hash table (as a state)
        r.hset(sub_key, mapping=event)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return {"status": "accepted", "req_id": req_id}


@app.get("/subscriptions/users/{user_id}")
async def get_user_subscription(user_id: str):
    data = r.hgetall(f"subscription:{user_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return data


# async def stream_events():
#     while True:
#         current_time = int(time.time())
#         message = f"data: Current time is {current_time}\n\n"
#         yield message
#         await asyncio.sleep(1)

# @app.get(
#     path="/events"
# )
# async def sse_stream_events():
#     return StreamingResponse(stream_events(), media_type="text/event-stream")