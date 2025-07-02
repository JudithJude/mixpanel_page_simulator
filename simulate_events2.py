import base64
import json
import time
import random
import requests
from datetime import datetime, timedelta

# ─── CONFIG ────────────────────────────────────────────────────────────────────
TOKEN        = "YOUR_PROJECT_TOKEN"
TRACK_URL    = "https://api.mixpanel.com/track/"
ENGAGE_URL   = "https://api.mixpanel.com/engage/"
NUM_USERS    = 50
MAX_DAYS     = 30     # spread events over the last MAX_DAYS days
PAUSE        = 0.05   # pause between events (seconds)

CITIES        = ["Lagos","New York","London","Berlin","Tokyo"]
COUNTRIES     = ["Nigeria","USA","UK","Germany","Japan"]
OPERATING_STYLES = ["B2C","B2B","Hybrid"]
# ────────────────────────────────────────────────────────────────────────────────

def send_track(event, props):
    """Send an event to Mixpanel track endpoint."""
    payload = {"event": event, "properties": {"token": TOKEN, **props}}
    data = base64.b64encode(json.dumps(payload).encode()).decode()
    resp = requests.post(TRACK_URL, params={"data": data})
    resp.raise_for_status()

def set_profile(uid, profile_props, ts):
    """Send a profile update via Mixpanel engage endpoint."""
    payload = {
        "$token": TOKEN,
        "$distinct_id": uid,
        "$time": ts,
        "$set": profile_props
    }
    data = base64.b64encode(json.dumps(payload).encode()).decode()
    resp = requests.post(ENGAGE_URL, params={"data": data})
    resp.raise_for_status()

def random_past_timestamp():
    """Return a UNIX timestamp anywhere in the last MAX_DAYS days."""
    now   = datetime.utcnow()
    delta = random.random() * MAX_DAYS
    past  = now - timedelta(days=delta)
    return int(past.timestamp())

for i in range(1, NUM_USERS+1):
    uid     = f"user_py_{i}"
    city    = random.choice(CITIES)
    country = random.choice(COUNTRIES)
    style   = random.choice(OPERATING_STYLES)
    ts_base = random_past_timestamp()

    # 1) Create user profile
    set_profile(uid,
                {"city": city, "country": country, "operating_style": style, "$name": uid},
                ts_base)
    print(f"[Profile] {uid} at {datetime.utcfromtimestamp(ts_base)} ({city}, {country}, {style})")
    time.sleep(PAUSE)

    # 2) Simulate full funnel events, 1 sec apart
    steps = [
        ("Page View",        {}),
        ("View Product",     {"product_id": f"prod_{i}"}),
        ("Add to Cart",      {"qty": 1}),
        ("Start Checkout",   {}),
        ("Purchase Completed",{"revenue": round(10 + i*0.5,2)})
    ]
    for idx, (evt, extra) in enumerate(steps):
        props = {
            "distinct_id": uid,
            "time": ts_base + idx,
            **extra
        }
        send_track(evt, props)
        print(f"[Event] {evt} for {uid} at {datetime.utcfromtimestamp(props['time'])}")
        time.sleep(PAUSE)

print(f"\n✅ Done: simulated full funnel & profiles for {NUM_USERS} users.")
