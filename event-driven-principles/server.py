import asyncio
import websockets


connected = set()

async def handler(websocket, path):
    connected.add(websocket)
    try:
        while True:
            message = await websocket.recv()
            await asyncio.gather(*[ws.send(message) for ws in connected])
    finally:
        connected.remove(websocket)


async def main():
    async with websockets.serve(handler, "localhost", 8000):
        await asyncio.Future()



asyncio.run(main())