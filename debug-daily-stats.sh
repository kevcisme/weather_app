#!/bin/bash

# Script to debug daily stats issue on Raspberry Pi

PI_HOST="192.168.86.49"
PI_USER="pi"

echo "🔍 Debugging Daily Stats Issue on Pi"
echo "====================================="
echo ""

echo "1️⃣  Checking if deployment succeeded..."
ssh ${PI_USER}@${PI_HOST} "cd /home/pi/actions-runner/_work/weather_app/weather_app && git log -1 --oneline"
echo ""

echo "2️⃣  Checking backend service status..."
ssh ${PI_USER}@${PI_HOST} "sudo systemctl status weather.service --no-pager | head -20"
echo ""

echo "3️⃣  Checking recent backend logs..."
echo "Looking for daily stats calculations..."
ssh ${PI_USER}@${PI_HOST} "journalctl -u weather.service -n 50 --no-pager | grep -i 'daily\|stats\|readings from'"
echo ""

echo "4️⃣  Testing /latest endpoint directly..."
ssh ${PI_USER}@${PI_HOST} "curl -s http://localhost:8000/latest | jq '{ts, daily_temp_min, daily_temp_max, daily_temp_avg, daily_humidity_avg, daily_pressure_avg}'"
echo ""

echo "5️⃣  Checking what date we're looking for..."
ssh ${PI_USER}@${PI_HOST} "date -u '+Today is: %Y-%m-%d (UTC)'"
echo ""

echo "6️⃣  Checking S3 bronze data for today..."
echo "This will show if we have readings from today..."
ssh ${PI_USER}@${PI_HOST} "cd /home/pi/actions-runner/_work/weather_app/weather_app/backend && source .venv/bin/activate && python3 -c \"
from src.weather.s3 import get_readings_from_bronze
from datetime import datetime, timezone
import sys

today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
readings = get_readings_from_bronze(hours=24)
today_readings = [r for r in readings if r['ts'].startswith(today)]

print(f'Total readings in last 24h: {len(readings)}')
print(f'Readings from today ({today}): {len(today_readings)}')
if today_readings:
    print(f'First reading: {today_readings[0][\"ts\"]}')
    print(f'Last reading: {today_readings[-1][\"ts\"]}')
    temps = [r['temp_f'] for r in today_readings]
    print(f'Temp range: {min(temps):.1f}°F - {max(temps):.1f}°F')
\""
echo ""

echo "✅ Diagnostic complete!"
echo ""
echo "If you see 0 readings from today, the issue is that there's no data in S3 for today yet."
echo "If readings exist but daily stats are null, there may be a code issue."

