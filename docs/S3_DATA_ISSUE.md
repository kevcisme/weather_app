# S3 Data Issue - Diagnosis & Fix

## Problem Summary

The `/history` endpoint isn't finding data because:

1. **Date Mismatch**: Your mock data files are from **October 6-7, 2025**
2. **Today's Date**: **October 10, 2025**
3. **Original Bug**: The code was only checking 2 dates (cutoff date + today), missing dates in between

## What I Fixed

### 1. **Backend S3 Query** (`backend/src/weather/s3.py`)
- ✅ Now checks ALL dates between cutoff and today
- ✅ Added debug logging to show what it's searching
- ✅ Shows count of readings found

### 2. **Frontend Date Validation**
- ✅ Validates timestamps before parsing (prevents crashes)
- ✅ Filters out invalid data
- ✅ Shows user-friendly error messages

## How to Fix the Data Problem

You have 3 options:

### Option 1: Generate Fresh Mock Data (Recommended)
SSH to your Pi and run:
```bash
ssh pi@192.168.86.49
cd ~/apps/raspi-weather-station/backend
uv run python upload_mock_data_to_s3.py --hours 72
```

This will:
- Generate 72 hours of mock data with **current timestamps**
- Upload it directly to S3 with proper folder structure
- Make it immediately available to your API

### Option 2: Use a Longer Time Range
Since your mock data is 3-4 days old, use:
- http://192.168.86.49:8000/history?hours=168 (7 days)

This will look back far enough to find the October 6-7 data.

### Option 3: Check What's Actually in S3
SSH to your Pi and run:
```bash
ssh pi@192.168.86.49
cd ~/apps/raspi-weather-station/backend
uv run python list_s3_objects.py
```

This will show you:
- What bucket and prefix are being used
- All files currently in S3
- Their timestamps and locations

## Restart Backend to See Debug Logs

After fixing the code, restart the backend service:
```bash
ssh pi@192.168.86.49
sudo systemctl restart weather
sudo journalctl -u weather -f
```

Then visit: http://192.168.86.49:8000/history?hours=24

You'll now see debug output like:
```
Fetching 24h history. Checking dates: ['2025-10-09', '2025-10-10']
Using bucket: manoa-raspi-weather, prefix: samples
No contents found for prefix: samples/2025-10-09/
No contents found for prefix: samples/2025-10-10/
Found 0 readings in last 24h
```

This will tell you exactly what's happening!

## Verify It Works

After uploading fresh data:
1. **Latest reading**: http://192.168.86.49:8000/latest
2. **24h history**: http://192.168.86.49:8000/history?hours=24
3. **Frontend**: http://192.168.86.49:3000

## S3 Folder Structure

Your data should be organized like:
```
s3://manoa-raspi-weather/
  samples/
    2025-10-10/
      2025-10-10T14-30-00.123456Z.json
      2025-10-10T15-30-00.123456Z.json
      ...
    2025-10-09/
      2025-10-09T14-30-00.123456Z.json
      ...
```

The code now correctly searches all dates in the requested time range!

