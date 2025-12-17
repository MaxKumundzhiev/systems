import sqlite3
import random

from datetime import datetime

from fastapi import FastAPI, status
from pydantic import BaseModel


app = FastAPI()


class Answer(BaseModel):
    text: str


class Feedback(BaseModel):
    answer_id: int
    rate: float
    feedback: str


@app.post("/answers/upload", status_code=status.HTTP_201_CREATED)
async def upload(request: Answer):
    id, now, text = random.randint(1, 10_000), datetime.now(), request.text
    with sqlite3.connect("answers.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO answers (id, content, created_at) VALUES (?, ?, ?)",
            (id, text, now)
        )
        connection.commit()
    return {"status": status.HTTP_201_CREATED, "id": id, "created_at": now}


@app.post("/answers/feedback", status_code=status.HTTP_201_CREATED)
async def feedback(request: Feedback):
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)