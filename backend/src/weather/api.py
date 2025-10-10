from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from .collector import read_measurement, create_silver_reading
from .settings import settings
from .s3 import get_readings_last_n_hours, get_latest_reading_from_s3, put_json_reading, put_silver_reading
import asyncio

app = FastAPI()

# Configure CORS to allow frontend to communicate with backend
# Allows local development and any IP access (for Raspberry Pi deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins since we're behind nginx in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def start():
    """
    Background task that uploads sensor readings to S3 every 15 minutes.
    Writes to both bronze (raw) and silver (enriched) layers.
    """
    async def upload_loop():
        while True:
            try:
                # Read raw measurement (bronze)
                bronze = read_measurement()
                put_json_reading(bronze)
                print(f"Bronze uploaded: {bronze['ts']}", flush=True)
                
                # Create and upload enriched silver reading
                silver = create_silver_reading(bronze)
                put_silver_reading(silver)
                print(f"Silver uploaded: {silver['ts']}", flush=True)
            except Exception as e:
                print(f"Error uploading to S3: {e}", flush=True)
            await asyncio.sleep(settings.sample_interval_sec)
    
    asyncio.create_task(upload_loop())

@app.get("/latest")
def get_latest():
    """
    Get the most recent weather reading from S3 silver layer.
    This represents the last stored measurement with calculated metrics.
    Daily stats are recalculated fresh from today's data from the silver layer.
    """
    from datetime import datetime, timezone
    from .calculations import calculate_daily_stats
    
    reading = get_latest_reading_from_s3()
    if reading is None:
        return {"error": "No readings found in S3"}
    
    # Recalculate daily stats from today's silver data (not bronze)
    # Silver data is already processed and more complete
    current_time = datetime.now(timezone.utc)
    today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Fetch last 24 hours to ensure we get all of today's readings
    # (We'll filter to today after fetching)
    todays_readings = get_readings_last_n_hours(hours=24)
    
    # Filter to only today's readings
    today_str = today_start.strftime("%Y-%m-%d")
    print(f"Looking for readings from today: {today_str}", flush=True)
    print(f"Fetched {len(todays_readings)} total readings", flush=True)
    
    # Show sample timestamps for debugging
    if todays_readings:
        print(f"Sample timestamps: {[r['ts'][:10] for r in todays_readings[:5]]}", flush=True)
    
    todays_readings = [r for r in todays_readings if r["ts"].startswith(today_str)]
    print(f"After filtering to today: {len(todays_readings)} readings", flush=True)
    
    # Calculate and update daily stats
    daily_stats = calculate_daily_stats(todays_readings)
    reading.update(daily_stats)
    
    # Debug logging
    print(f"Daily stats - min: {daily_stats.get('daily_temp_min')}, max: {daily_stats.get('daily_temp_max')}, avg: {daily_stats.get('daily_temp_avg')}", flush=True)
    
    return reading

@app.get("/current")
def get_current():
    """
    Get a real-time reading directly from the sensor with calculated metrics.
    This reading is NOT stored in S3 - it's captured at the moment of the request.
    """
    try:
        bronze = read_measurement()
        silver = create_silver_reading(bronze)
        return silver
    except Exception as e:
        return {"error": f"Failed to read sensor: {str(e)}"}

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
