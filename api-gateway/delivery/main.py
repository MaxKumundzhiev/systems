from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "Delivery service healthy"}


@app.get("/users/{user_id}/delivery")
async def list_deliveries(user_id: str):
    return {
        "user_id": user_id,
        "operation": "LIST_ALL_DELIVERIES",
        "deliveries": [
            {"id": 1, "date": "2024-01-01"},
            {"id": 2, "date": "2024-01-01"},
            {"id": 3, "date": "2024-01-03"}
        ]
    }