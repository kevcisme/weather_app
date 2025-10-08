from pydantic import BaseModel
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the same directory as this file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseModel):
    # AWS Credentials
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-west-2")
    
    # S3 Configuration
    s3_bucket: str = os.getenv("S3_BUCKET", "manoa-raspi-weather")
    s3_prefix: str = os.getenv("S3_PREFIX", "samples")
    
    # Application Configuration
    sample_interval_sec: int = int(os.getenv("SAMPLE_INTERVAL_SEC", "900")) # i picked every 15 minutes here, just because round
    
    # Sensor Calibration
    # Static temperature offset in Celsius to subtract from pressure sensor reading
    # This compensates for ambient heat from the Pi board
    temp_calibration_offset_c: float = float(os.getenv("TEMP_CALIBRATION_OFFSET_C", "12.0"))
    
    # Dynamic CPU temperature compensation (advanced)
    use_cpu_compensation: bool = os.getenv("USE_CPU_COMPENSATION", "true").lower() == "true"
    cpu_temp_factor_c: float = float(os.getenv("CPU_TEMP_FACTOR_C", "2.0"))

settings = Settings()
