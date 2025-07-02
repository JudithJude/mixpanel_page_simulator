import base64
import json
import time
import requests

TOKEN = "3fa2c64f2b6a4115e5407bd26b1ca9c3"
URL   = "https://api.mixpanel.com/track/"
NUM   = 50
DELAY = 0.1  # seconds

def send(event, props):
    data = base64.b64encode(json.dumps({
        "event": event,
        "properties": { "token": TOKEN, **props }
    }).encode()).decode()
    resp = requests.post(URL, params={"data": data})
    resp.raise_for_status()

for i in range(1, NUM+1):
    uid = f"user_py_{i}"
    send("Page View",        {"distinct_id": uid})
    send("View Product",     {"distinct_id": uid, "product_id": f"prod_{i}"})
    send("Add to Cart",      {"distinct_id": uid, "qty": 1})
    send("Start Checkout",   {"distinct_id": uid})
    send("Purchase Completed",{"distinct_id": uid, "revenue": i * 1.5})
    print(f"Simulated user {i}")
    time.sleep(DELAY)

print(f"Done: simulated full funnel for {NUM} users.")
