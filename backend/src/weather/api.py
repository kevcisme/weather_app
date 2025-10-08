from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from .collector import read_measurement
from .settings import settings
from .s3 import get_readings_last_n_hours
import asyncio

app = FastAPI()

# Configure CORS to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Add your production domain here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest = {}

@app.on_event("startup")
async def start():
    async def loop():
        global latest
        while True:
            try:
                # Use the same measurement logic as the collector
                latest = read_measurement()
                # Note: S3 upload is done by the separate collector service
                print(f"Updated reading: {latest['ts']}", flush=True)
            except Exception as e:
                print(f"Error reading sensor data: {e}")
            await asyncio.sleep(settings.sample_interval_sec)
    
    # Populate initial data immediately
    try:
        global latest
        latest = read_measurement()
    except Exception as e:
        print(f"Error initializing sensor data: {e}")
    
    asyncio.create_task(loop())

@app.get("/latest")
def get_latest():
    return latest

@app.get("/history")
def get_history(
    hours: int = Query(default=24, ge=1, le=168, description="Number of hours to look back (1-168)")
):
    """
    Retrieve weather readings from the last N hours.
    
    Args:
        hours: Number of hours to look back (default: 24, max: 168/7 days)
    
    Returns:
        Readings sorted by timestamp (oldest first).
    """
    try:
        readings = get_readings_last_n_hours(hours)
        return {
            "hours": hours,
            "count": len(readings),
            "readings": readings
        }
    except Exception as e:
        print(f"Error retrieving {hours}h history: {e}", flush=True)
        return {
            "error": str(e),
            "hours": hours,
            "count": 0,
            "readings": []
        }
