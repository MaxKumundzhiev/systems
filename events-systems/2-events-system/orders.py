from fastapi import FastAPI


app = FastAPI(title="orders")


@app.get("/orders")
async def list_orders():
    return []
