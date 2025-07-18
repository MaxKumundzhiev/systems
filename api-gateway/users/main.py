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
    return {"status": "Users service healthy"}


@app.get("/users/{id}")
async def user(id: str):
    return {
        "id": id,
        "name": "Max",
        "surname": "Doe",
        "email": "foo@gmail.com"
    }