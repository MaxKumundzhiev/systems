import httpx
import time
from random import randint, random
from datetime import datetime

if __name__ == "__main__":
    while True:
        with httpx.Client() as client:
            payload = {
                "total_price": randint(20, 200),
                "order_time": datetime.now().isoformat(),
            }
            r = client.post(url="http://0.0.0.0:8000/orders", json=payload)
            print(r)
            time.sleep(random())
