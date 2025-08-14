import os
import time
import asyncio
from typing import Dict, List, Tuple, Optional, Literal

import httpx
from pydantic import BaseModel, ValidationError
from redis.asyncio import Redis


# ---------------------- config ----------------------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
STREAM = os.getenv("STREAM", "events:subscriptions")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://127.0.0.1:8000/webhook/subscription-created")

START_ID = os.getenv("START_ID", "$")         # "$" → только новые; "0-0" → вся история
BATCH_COUNT = int(os.getenv("BATCH_COUNT", "32"))
BLOCK_MS = int(os.getenv("BLOCK_MS", "5000"))

r: Redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


# ---------------------- models ----------------------
Status = Literal["PENDING", "CREATED"]
EventType = Literal["NEW_SUBSCRIPTION", "CREATED_SUBSCRIPTION"]

class Event(BaseModel):
    req_id: str
    user_id: str
    tier_id: str
    last_req_id: str
    status: Status
    event: EventType
    created_at: str  # unix ts as string
    updated_at: str  # unix ts as string
    version: str

class SubscriptionSnapshot(BaseModel):
    req_id: str
    user_id: str
    tier_id: str
    last_req_id: str
    status: Status
    event: EventType
    created_at: str
    updated_at: str
    version: str

class WebhookPayload(BaseModel):
    event: EventType
    status: Status
    user_id: str
    tier_id: str
    req_id: str
    created_at: str
    updated_at: str
    version: str


# ---------------------- business logic ----------------------
async def process_event(ev: Event) -> Event:
    """Имитация работы + перевод PENDING -> CREATED."""
    await asyncio.sleep(0.2)
    # обновляем статус/ивент/время
    ev = ev.copy(update={
        "status": "CREATED",
        "event": "CREATED_SUBSCRIPTION",
        "updated_at": str(int(time.time())),
        "last_req_id": ev.req_id,  # на всякий случай синхронизируем
    })
    return ev

def snapshot_from_event(ev: Event, existing_created_at: Optional[str]) -> SubscriptionSnapshot:
    """Строим снапшот для hash. created_at не перезатираем, если уже был."""
    created = existing_created_at or ev.created_at or str(int(time.time()))
    return SubscriptionSnapshot(
        req_id=ev.req_id,
        user_id=ev.user_id,
        tier_id=ev.tier_id,
        last_req_id=ev.last_req_id,
        status=ev.status,
        event=ev.event,
        created_at=created,
        updated_at=ev.updated_at,
        version=ev.version,
    )

def webhook_from_event(ev: Event) -> WebhookPayload:
    return WebhookPayload(
        event=ev.event,
        status=ev.status,
        user_id=ev.user_id,
        tier_id=ev.tier_id,
        req_id=ev.req_id,
        created_at=ev.created_at,
        updated_at=ev.updated_at,
        version=ev.version,
    )

# ---------------------- side effects ----------------------
async def update_status_in_hash(snapshot: SubscriptionSnapshot) -> None:
    key = f"subscription:{snapshot.user_id}"
    await r.hset(key, mapping=snapshot.model_dump())

async def send_webhook(payload: WebhookPayload) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(WEBHOOK_URL, json=payload.model_dump())
        resp.raise_for_status()

# ---------------------- worker loop (no groups) ----------------------
async def handler() -> None:
    last_id: str = START_ID
    print(f"[worker] listening stream={STREAM} from last_id={last_id}")

    while True:
        try:
            # XREAD → [(stream_key, [(msg_id, {field: val, ...}), ...])]
            resp: List[Tuple[str, List[Tuple[str, Dict[str, str]]]]] = await r.xread(
                streams={STREAM: last_id},
                count=BATCH_COUNT,
                block=BLOCK_MS
            )
            if not resp:
                continue

            _, entries = resp[0]
            for msg_id, fields in entries:
                # 1) валидируем входной ивент
                try:
                    ev = Event(**fields)
                except ValidationError as ve:
                    print("[worker] bad event, skip:", ve, fields)
                    last_id = msg_id
                    continue

                # (опц.) фильтр по контракту
                if ev.status != "PENDING" or ev.event != "NEW_SUBSCRIPTION":
                    last_id = msg_id
                    continue

                # 2) бизнес-обработка
                try:
                    ev = await process_event(ev)
                except Exception as e:
                    print("[worker] process_event error:", e, ev.model_dump())
                    last_id = msg_id
                    continue

                # 3) снапшот и hash
                try:
                    existing_created = await r.hget(f"subscription:{ev.user_id}", "created_at")
                    snapshot = snapshot_from_event(ev, existing_created)
                    await update_status_in_hash(snapshot)
                except Exception as e:
                    print("[worker] update_status_in_hash error:", e, ev.model_dump())
                    last_id = msg_id
                    continue

                # 4) webhook
                try:
                    await send_webhook(webhook_from_event(ev))
                except Exception as e:
                    print("[worker] webhook error:", e, ev.model_dump())

                # 5) двигаем курсор всегда (без групп нет ack/pending)
                last_id = msg_id

        except Exception as e:
            print("[worker] redis/read error:", e)
            await asyncio.sleep(0.5)

# ---------------------- entrypoint ----------------------
if __name__ == "__main__":
    asyncio.run(handler())
