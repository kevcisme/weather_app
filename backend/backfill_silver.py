#!/usr/bin/env python3
"""
Backfill script to regenerate silver layer data from bronze layer.

This script reads raw sensor data from the bronze layer (samples/) and
recalculates all silver layer metrics (dew point, pressure trends, daily stats).

Usage:
    python backfill_silver.py --days 7  # Backfill last 7 days
    python backfill_silver.py --days 1 --dry-run  # Preview without writing
"""

import argparse
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict

# Import our modules
from src.weather.s3 import _s3, put_silver_reading
from src.weather.settings import settings
from src.weather.calculations import (
    calculate_dew_point,
    calculate_pressure_trend,
    calculate_daily_stats,
    get_comfort_index
)


def fetch_bronze_readings_for_period(start_date: datetime, end_date: datetime) -> List[Dict]:
    """
    Fetch all bronze layer readings for a date range.
    
    Args:
        start_date: Start of period (inclusive)
        end_date: End of period (inclusive)
    
    Returns:
        List of bronze readings sorted by timestamp
    """
    readings = []
    current = start_date
    
    # Generate all dates in the range
    dates_to_check = []
    while current <= end_date:
        dates_to_check.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    print(f"📦 Fetching bronze data for {len(dates_to_check)} day(s): {dates_to_check[0]} to {dates_to_check[-1]}")
    
    for date in dates_to_check:
        prefix = f"{settings.s3_prefix}/{date}/"
        
        try:
            paginator = _s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=settings.s3_bucket, Prefix=prefix)
            
            count = 0
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    key = obj['Key']
                    
                    try:
                        response = _s3.get_object(Bucket=settings.s3_bucket, Key=key)
                        data = json.loads(response['Body'].read().decode('utf-8'))
                        
                        # Parse timestamp and filter by date range
                        reading_time = datetime.fromisoformat(data['ts'].replace('Z', '+00:00'))
                        
                        if start_date <= reading_time <= end_date:
                            readings.append(data)
                            count += 1
                    
                    except Exception as e:
                        print(f"⚠️  Error reading {key}: {e}")
                        continue
            
            if count > 0:
                print(f"  ✓ {date}: {count} readings")
        
        except Exception as e:
            print(f"⚠️  Error listing objects for {date}: {e}")
            continue
    
    # Sort by timestamp
    readings.sort(key=lambda x: x['ts'])
    
    print(f"✓ Total bronze readings fetched: {len(readings)}\n")
    return readings


def create_silver_reading_backfill(
    bronze_reading: Dict, 
    all_readings_for_trends: List[Dict],
    daily_readings: List[Dict]
) -> Dict:
    """
    Create enriched silver reading from bronze data with calculated metrics.
    
    Args:
        bronze_reading: Raw sensor reading
        all_readings_for_trends: Historical readings for pressure trend calculation
        daily_readings: All readings from the same day for daily stats
    
    Returns:
        Enriched reading with calculated metrics
    """
    silver = bronze_reading.copy()
    
    # 1. Calculate dew point
    dew_point = calculate_dew_point(bronze_reading["temp_c"], bronze_reading["humidity"])
    silver.update(dew_point)
    
    # 2. Calculate comfort index
    silver["comfort_index"] = get_comfort_index(
        bronze_reading["temp_f"], 
        bronze_reading["humidity"],
        dew_point["dew_point_f"]
    )
    
    # 3. Calculate pressure trend
    pressure_trend = calculate_pressure_trend(bronze_reading, all_readings_for_trends)
    silver.update(pressure_trend)
    
    # 4. Calculate daily stats
    daily_stats = calculate_daily_stats(daily_readings)
    silver.update(daily_stats)
    
    return silver


def backfill_silver_layer(days: int, dry_run: bool = False) -> Dict[str, int]:
    """
    Main backfill function.
    
    Args:
        days: Number of days to backfill
        dry_run: If True, preview without writing
    
    Returns:
        Statistics dictionary
    """
    # Calculate date range
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days)
    
    print(f"{'🔍 DRY RUN MODE' if dry_run else '🚀 BACKFILL MODE'}")
    print(f"Period: {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bronze source: s3://{settings.s3_bucket}/{settings.s3_prefix}/")
    print(f"Silver target: s3://{settings.s3_bucket}/{settings.s3_silver_prefix}/")
    print()
    
    # Fetch all bronze readings for the period
    bronze_readings = fetch_bronze_readings_for_period(start_time, end_time)
    
    if not bronze_readings:
        print("❌ No bronze readings found for this period!")
        return {"total": 0, "processed": 0, "written": 0, "errors": 0}
    
    # Group readings by date for daily stats calculation
    readings_by_date = defaultdict(list)
    for reading in bronze_readings:
        date_str = reading["ts"][:10]  # Extract YYYY-MM-DD
        readings_by_date[date_str].append(reading)
    
    print(f"📊 Processing {len(bronze_readings)} readings across {len(readings_by_date)} days\n")
    
    # Statistics
    stats = {
        "total": len(bronze_readings),
        "processed": 0,
        "written": 0,
        "errors": 0,
        "skipped": 0
    }
    
    # Process each reading
    for idx, bronze in enumerate(bronze_readings):
        try:
            reading_time = datetime.fromisoformat(bronze['ts'].replace('Z', '+00:00'))
            date_str = bronze["ts"][:10]
            
            # Get historical context for pressure trends (look back 7 hours)
            lookback_time = reading_time - timedelta(hours=7)
            historical_readings = [
                r for r in bronze_readings 
                if lookback_time <= datetime.fromisoformat(r['ts'].replace('Z', '+00:00')) < reading_time
            ]
            
            # Get all readings from same day for daily stats
            # Filter to only readings up to current time (for accurate rolling stats)
            daily_readings = [
                r for r in readings_by_date[date_str]
                if datetime.fromisoformat(r['ts'].replace('Z', '+00:00')) <= reading_time
            ]
            
            # Create silver reading with all calculations
            silver = create_silver_reading_backfill(bronze, historical_readings, daily_readings)
            
            stats["processed"] += 1
            
            # Write to S3 (unless dry run)
            if not dry_run:
                put_silver_reading(silver)
                stats["written"] += 1
            
            # Progress indicator
            if (idx + 1) % 100 == 0 or (idx + 1) == len(bronze_readings):
                progress = (idx + 1) / len(bronze_readings) * 100
                print(f"Progress: {idx + 1}/{len(bronze_readings)} ({progress:.1f}%) - "
                      f"Latest: {bronze['ts']}", end='\r')
        
        except Exception as e:
            print(f"\n⚠️  Error processing reading {bronze.get('ts', 'unknown')}: {e}")
            stats["errors"] += 1
            continue
    
    print()  # New line after progress indicator
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Backfill silver layer data from bronze layer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Backfill last 7 days
  python backfill_silver.py --days 7
  
  # Preview what would be backfilled for last 24 hours
  python backfill_silver.py --days 1 --dry-run
  
  # Backfill entire history (max 30 days)
  python backfill_silver.py --days 30
        """
    )
    
    parser.add_argument(
        '--days',
        type=int,
        required=True,
        help='Number of days to backfill (1-30)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without writing to S3'
    )
    
    args = parser.parse_args()
    
    # Validate
    if args.days < 1 or args.days > 30:
        print("❌ Error: --days must be between 1 and 30")
        return 1
    
    print("=" * 70)
    print("  SILVER LAYER BACKFILL TOOL")
    print("=" * 70)
    print()
    
    # Run backfill
    stats = backfill_silver_layer(args.days, args.dry_run)
    
    # Print summary
    print()
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"Total readings:     {stats['total']}")
    print(f"Processed:          {stats['processed']}")
    print(f"Written to silver:  {stats['written']}")
    print(f"Errors:             {stats['errors']}")
    
    if args.dry_run:
        print()
        print("✅ Dry run completed successfully!")
        print("   Run without --dry-run to write to S3")
    else:
        print()
        print("✅ Backfill completed successfully!")
        print(f"   Silver layer updated: s3://{settings.s3_bucket}/{settings.s3_silver_prefix}/")
    
    return 0 if stats['errors'] == 0 else 1


if __name__ == "__main__":
    exit(main())

