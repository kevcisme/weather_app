import time, json
from datetime import datetime, timezone
from .hat import get_sense
from .s3 import put_json_reading
from .settings import settings

sense = get_sense()

def read_measurement():
    return {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "temp_c": round(sense.get_temperature(), 2),
        "temp_f": round(1.8 * sense.get_temperature() + 32, 2),
        "humidity": round(sense.get_humidity(), 2),
        "pressure": round(sense.get_pressure(), 2),
    }

if __name__ == "__main__":
    while True:
        d = read_measurement()
        print(json.dumps(d), flush=True)
        try:
            put_json_reading(d)
        except Exception as e:
            print(f"S3 upload error: {e}", flush=True)
        time.sleep(settings.sample_interval_sec)
