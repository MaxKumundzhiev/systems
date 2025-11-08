from fastapi import FastAPI


app = FastAPI()

db = {
    "123": {"name": "laptop", "qnt": 10},
    "321": {"name": "phone", "qnt": 5},
    "100": {"name": "bicycle", "qnt": 90},
}

@app.get("/items")
async def get():
    return db



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)