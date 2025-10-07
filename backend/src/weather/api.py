from fastapi import FastAPI
from datetime import datetime, timezone
from .hat import get_sense
from .settings import settings
from .s3 import put_json_reading
import asyncio

app = FastAPI()
sense = get_sense()
latest = {}

@app.on_event("startup")
async def start():
    async def loop():
        global latest
        while True:
            try:
                latest = {
                    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
                    "temp_c": round(sense.get_temperature(),2),
                    "temp_f": round(1.8 * sense.get_temperature() + 32, 2),
                    "humidity": round(sense.get_humidity(),2),
                    "pressure": round(sense.get_pressure(),2),
                }
                # Upload to S3
                try:
                    put_json_reading(latest)
                    print(f"Uploaded to S3: {latest['ts']}", flush=True)
                except Exception as e:
                    print(f"S3 upload error: {e}", flush=True)
            except Exception as e:
                print(f"Error reading sensor data: {e}")
            await asyncio.sleep(settings.sample_interval_sec)
    
    # Populate initial data immediately
    try:
        global latest
        latest = {
            "ts": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
            "temp_c": round(sense.get_temperature(),2),
            "temp_f": round(1.8 * sense.get_temperature() + 32, 2),
            "humidity": round(sense.get_humidity(),2),
            "pressure": round(sense.get_pressure(),2),
        }
    except Exception as e:
        print(f"Error initializing sensor data: {e}")
    
    asyncio.create_task(loop())

@app.get("/latest")
def get_latest():
    return latest
