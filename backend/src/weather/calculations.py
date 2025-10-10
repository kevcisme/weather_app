"""
Weather calculations and derived metrics.
Supports the silver layer of the medallion architecture.
"""
import math
from datetime import datetime, timezone
from typing import Optional


def calculate_dew_point(temp_c: float, humidity: float) -> dict:
    """
    Calculate dew point using the Magnus formula.
    
    Args:
        temp_c: Temperature in Celsius
        humidity: Relative humidity as percentage (0-100)
    
    Returns:
        Dictionary with dew_point_c and dew_point_f
    """
    # Magnus formula constants
    a = 17.27
    b = 237.7
    
    # Calculate alpha
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    
    # Calculate dew point in Celsius
    dew_point_c = (b * alpha) / (a - alpha)
    dew_point_f = dew_point_c * 1.8 + 32
    
    return {
        "dew_point_c": round(dew_point_c, 2),
        "dew_point_f": round(dew_point_f, 2)
    }


def calculate_pressure_trend(current_reading: dict, historical_readings: list[dict]) -> dict:
    """
    Calculate pressure trend over 3h and 6h periods.
    
    Args:
        current_reading: Current weather reading with ts and pressure
        historical_readings: List of historical readings (should include last 6+ hours)
    
    Returns:
        Dictionary with pressure trend metrics
    """
    if not historical_readings:
        return {
            "pressure_trend_3h": None,
            "pressure_trend_6h": None,
            "pressure_trend_label": "unknown"
        }
    
    current_time = datetime.fromisoformat(current_reading["ts"].replace("Z", "+00:00"))
    current_pressure = current_reading["pressure"]
    
    # Find readings closest to 3h and 6h ago
    pressure_3h_ago = None
    pressure_6h_ago = None
    
    for reading in historical_readings:
        reading_time = datetime.fromisoformat(reading["ts"].replace("Z", "+00:00"))
        hours_ago = (current_time - reading_time).total_seconds() / 3600
        
        # Find reading closest to 3 hours ago (within ±30 min window)
        if 2.5 <= hours_ago <= 3.5 and pressure_3h_ago is None:
            pressure_3h_ago = reading["pressure"]
        
        # Find reading closest to 6 hours ago (within ±30 min window)
        if 5.5 <= hours_ago <= 6.5 and pressure_6h_ago is None:
            pressure_6h_ago = reading["pressure"]
    
    # Calculate trends (positive = rising, negative = falling)
    trend_3h = round(current_pressure - pressure_3h_ago, 2) if pressure_3h_ago else None
    trend_6h = round(current_pressure - pressure_6h_ago, 2) if pressure_6h_ago else None
    
    # Determine trend label based on 3h trend (or 6h if 3h not available)
    trend_value = trend_3h if trend_3h is not None else trend_6h
    
    if trend_value is None:
        label = "unknown"
    elif trend_value < -3:
        label = "rapidly_falling"
    elif trend_value < -1:
        label = "falling"
    elif trend_value <= 1:
        label = "steady"
    elif trend_value <= 3:
        label = "rising"
    else:
        label = "rapidly_rising"
    
    return {
        "pressure_trend_3h": trend_3h,
        "pressure_trend_6h": trend_6h,
        "pressure_trend_label": label
    }


def calculate_daily_stats(todays_readings: list[dict]) -> dict:
    """
    Calculate rolling daily statistics from today's readings.
    
    Args:
        todays_readings: All readings from today (00:00 UTC to now)
    
    Returns:
        Dictionary with daily min/max/avg values
    """
    if not todays_readings:
        return {
            "daily_temp_min": None,
            "daily_temp_max": None,
            "daily_temp_avg": None,
            "daily_humidity_avg": None,
            "daily_pressure_avg": None
        }
    
    temps = [r["temp_f"] for r in todays_readings if "temp_f" in r]
    humidities = [r["humidity"] for r in todays_readings if "humidity" in r]
    pressures = [r["pressure"] for r in todays_readings if "pressure" in r]
    
    return {
        "daily_temp_min": round(min(temps), 1) if temps else None,
        "daily_temp_max": round(max(temps), 1) if temps else None,
        "daily_temp_avg": round(sum(temps) / len(temps), 1) if temps else None,
        "daily_humidity_avg": round(sum(humidities) / len(humidities), 1) if humidities else None,
        "daily_pressure_avg": round(sum(pressures) / len(pressures), 1) if pressures else None
    }


def get_comfort_index(temp_f: float, humidity: float, dew_point_f: float) -> str:
    """
    Determine comfort index based on temperature, humidity, and dew point.
    
    Returns:
        String describing comfort level: "comfortable", "too_dry", "too_humid", "too_cold", "too_hot"
    """
    # Temperature-based comfort
    if temp_f < 60:
        return "too_cold"
    elif temp_f > 80:
        return "too_hot"
    
    # Humidity-based comfort
    if humidity < 30:
        return "too_dry"
    elif dew_point_f > 65:
        return "too_humid"
    elif humidity > 70:
        return "too_humid"
    
    return "comfortable"

