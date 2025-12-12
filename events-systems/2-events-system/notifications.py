from fastapi import FastAPI


app = FastAPI(title="notifications")


@app.get("/notifications")
async def list_orders():
    return []
