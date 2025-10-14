# Silver Layer Backfill Guide

This guide explains how to use the backfill script to regenerate silver layer data from bronze layer readings.

## When to Use Backfill

You should run the backfill script when:

1. **Service Outage**: The collection service went down and silver writes failed, but bronze data was still collected
2. **New Metrics Added**: You add new calculated metrics and want to apply them to historical data
3. **Bug Fixes**: You fixed a bug in calculations and want to reprocess historical data
4. **Silver Data Loss**: The silver bucket/folder was accidentally deleted or corrupted

## How It Works

The backfill script:
1. Reads raw sensor data from the **bronze layer** (`samples/` folder in S3)
2. For each bronze reading, it calculates:
   - Dew point (using temperature and humidity)
   - Pressure trends (3h and 6h changes)
   - Daily statistics (min/max/avg for the day)
   - Comfort index
3. Writes enriched data to the **silver layer** (`silver/` folder in S3)

**Important**: The script processes readings in chronological order to ensure accurate rolling calculations (especially for daily stats and pressure trends).

## Usage

### Basic Syntax

```bash
cd backend
python backfill_silver.py --days N [--dry-run]
```

### Parameters

- `--days N`: Number of days to backfill (1-30)
- `--dry-run`: Preview what would be processed without writing to S3

### Examples

#### Example 1: Preview Last 24 Hours
```bash
python backfill_silver.py --days 1 --dry-run
```

This will:
- Show you what data would be processed
- Display statistics
- **Not write anything** to S3

#### Example 2: Backfill Last 7 Days
```bash
python backfill_silver.py --days 7
```

This will:
- Process all bronze readings from the last 7 days
- Calculate silver metrics for each reading
- Write enriched data to silver layer
- Show progress as it runs

#### Example 3: Full Historical Backfill
```bash
python backfill_silver.py --days 30
```

Processes the maximum allowed time period (30 days).

## Output

The script provides detailed output:

```
======================================================================
  SILVER LAYER BACKFILL TOOL
======================================================================

🚀 BACKFILL MODE
Period: 2025-10-03 10:00:00 to 2025-10-10 10:00:00
Bronze source: s3://manoa-raspi-weather/samples/
Silver target: s3://manoa-raspi-weather/silver/

📦 Fetching bronze data for 7 day(s): 2025-10-03 to 2025-10-10
  ✓ 2025-10-03: 96 readings
  ✓ 2025-10-04: 96 readings
  ...
✓ Total bronze readings fetched: 672

📊 Processing 672 readings across 7 days

Progress: 672/672 (100.0%) - Latest: 2025-10-10T10:00:00Z

======================================================================
  SUMMARY
======================================================================
Total readings:     672
Processed:          672
Written to silver:  672
Errors:             0

✅ Backfill completed successfully!
   Silver layer updated: s3://manoa-raspi-weather/silver/
```

## Best Practices

### 1. Always Dry Run First
```bash
python backfill_silver.py --days 7 --dry-run
```
This lets you verify:
- The date range is correct
- Bronze data exists for that period
- Expected number of readings

### 2. Start Small
If backfilling a long period, start with a smaller test:
```bash
# Test with 1 day first
python backfill_silver.py --days 1

# Then do the full backfill
python backfill_silver.py --days 30
```

### 3. Check AWS Credentials
Make sure your `.env` file has correct AWS credentials:
```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-west-2
S3_BUCKET=manoa-raspi-weather
```

### 4. Monitor Progress
The script shows real-time progress. For large backfills:
- Processing ~10-20 readings/second is normal
- 1 day (96 readings) takes ~10 seconds
- 7 days (~672 readings) takes ~1 minute
- 30 days (~2,880 readings) takes ~5 minutes

## Troubleshooting

### No Bronze Readings Found
```
❌ No bronze readings found for this period!
```

**Cause**: Bronze layer doesn't have data for the requested period.

**Solution**: 
- Check if data exists in S3: `aws s3 ls s3://manoa-raspi-weather/samples/`
- Reduce `--days` parameter
- Verify the collection service is running

### AWS Credentials Error
```
botocore.exceptions.NoCredentialsError
```

**Solution**: 
1. Check `.env` file exists in `backend/src/weather/`
2. Verify AWS credentials are correct
3. Test with: `python -c "from src.weather.settings import settings; print(settings.aws_access_key_id)"`

### Partial Errors
```
⚠️  Error processing reading 2025-10-05T12:30:00Z: ...
```

**Cause**: Individual readings might be corrupted or missing required fields.

**Solution**: The script continues processing. Check the summary:
- If errors < 5%: Normal, some readings may be corrupt
- If errors > 5%: Investigate bronze data quality

## Running on Raspberry Pi

When SSH'd into your Pi:

```bash
cd ~/weather_app/backend

# Activate environment if needed
source venv/bin/activate  # or your venv path

# Run backfill
python backfill_silver.py --days 7
```

## Automation

You can schedule periodic backfills to ensure consistency:

```bash
# Add to crontab (runs daily at 3 AM, backfills last 2 days)
0 3 * * * cd /home/pi/weather_app/backend && python backfill_silver.py --days 2 >> /var/log/weather_backfill.log 2>&1
```

## Technical Notes

### Date Handling
- All dates are in UTC
- The script is timezone-aware
- Daily stats are calculated based on UTC day boundaries

### Performance
- Bronze data is fetched in bulk (efficient)
- Readings are processed sequentially (ensures accuracy)
- Progress updates every 100 readings

### Data Integrity
- Existing silver files are **overwritten** (not duplicated)
- Bronze layer is **never modified** (read-only)
- Failed reads are logged but don't stop the process

## FAQ

**Q: Can I backfill while the collection service is running?**  
A: Yes! The backfill reads from bronze and writes to silver. It won't interfere with ongoing collection.

**Q: What if I run backfill twice for the same period?**  
A: It's safe. Silver files will be overwritten with the same calculated values.

**Q: Will this affect my frontend?**  
A: No downtime. The frontend reads from silver, and S3 operations are atomic.

**Q: Can I backfill specific hours instead of days?**  
A: Currently no, but you can modify the script to add `--start-date` and `--end-date` parameters.

**Q: How do I verify the backfill worked?**  
A: 
```bash
# Check silver folder in S3
aws s3 ls s3://manoa-raspi-weather/silver/2025-10-10/

# Or check via frontend - reload the page and check if metrics appear
```

## Support

If you encounter issues:
1. Run with `--dry-run` first
2. Check the error message
3. Verify AWS/S3 connectivity: `aws s3 ls s3://manoa-raspi-weather/`
4. Check logs if running as cron job

