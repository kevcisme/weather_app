# Weather Station Application

A full-stack weather monitoring application with real-time data collection, S3 storage, and beautiful visualization dashboard.

## Architecture

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────┐
│   Raspberry Pi  │       │   FastAPI        │       │   Next.js   │
│   (Sense HAT)   │──────▶│   Backend        │◀──────│   Frontend  │
│                 │       │                  │       │  Dashboard  │
└─────────────────┘       └────────┬─────────┘       └─────────────┘
                                   │
                                   │ Uploads readings
                                   │ Fetches history
                                   ▼
                          ┌─────────────────┐
                          │   AWS S3        │
                          │ Medallion Arch  │
                          │  Bronze│Silver  │
                          └─────────────────┘
```

### Medallion Architecture

The application uses a **medallion architecture** pattern with two data layers:

- **Bronze Layer** (`samples/`): Raw sensor readings, source of truth
- **Silver Layer** (`silver/`): Enriched data with calculated metrics
  - Dew point (temperature + humidity)
  - Pressure trends (3h/6h changes)
  - Daily statistics (min/max/avg)
  - Comfort index

This architecture provides:
- **Data quality**: Raw data always preserved
- **Flexibility**: Easy to add new metrics via backfill
- **Performance**: Pre-calculated metrics for fast queries
- **Recovery**: Can regenerate silver layer from bronze anytime

## Features

### Backend (FastAPI + Python)
- 🌡️ Real-time sensor data collection from Raspberry Pi Sense HAT
- ☁️ Automatic upload to AWS S3 with organized date-based structure
- 📊 RESTful API endpoints for current and historical data
- ⚙️ Configurable sampling intervals
- 🔒 Environment-based configuration
- 🏗️ Medallion architecture (bronze/silver layers)
- 🔄 Backfill utility for regenerating metrics
- 📈 Advanced metrics: dew point, pressure trends, daily stats

### Frontend (Next.js + TypeScript)
- 📱 Responsive, modern dashboard interface
- 📈 Interactive charts for temperature, humidity, and pressure
- ⏱️ Real-time updates (auto-refresh every 60 seconds)
- 📅 Flexible time range selection (1 hour to 7 days)
- 🎨 Beautiful UI built with Shadcn UI and Tailwind CSS
- 🌡️ Dew point display with comfort indicators
- 📊 Pressure trend visualization with weather forecasting
- 📋 Daily summary statistics

## Quick Start

### Prerequisites
- Python 3.11+ with uv package manager
- Node.js 18+ and npm
- AWS account with S3 bucket
- Raspberry Pi with Sense HAT (or use emulator for testing)

### 1. Backend Setup

```bash
cd backend

# Create .env file from environment variables
cat > src/weather/.env << EOF
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-west-2
S3_BUCKET=your-bucket-name
S3_PREFIX=samples
SAMPLE_INTERVAL_SEC=900
EOF

# Install dependencies
uv sync

# Run the API server
uv run uvicorn weather.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**API Endpoints:**
- `GET /latest` - Current weather reading
- `GET /history?hours=24` - Historical readings (1-168 hours)

### 2. Frontend Setup

```bash
cd frontend

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Install dependencies
npm install

# Run the development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## Project Structure

```
weather_app/
├── backend/
│   ├── src/weather/
│   │   ├── api.py              # FastAPI application
│   │   ├── collector.py        # Data collection logic
│   │   ├── s3.py              # S3 integration
│   │   ├── settings.py        # Configuration
│   │   └── hat.py             # Sense HAT interface
│   ├── mock_data/             # Sample data for testing
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js pages
│   │   ├── components/        # React components
│   │   └── lib/               # Utilities and API client
│   └── package.json
│
└── deploy/                    # Deployment scripts
```

## Data Format

### Bronze Layer (Raw Sensor Data)
Weather readings are stored as JSON in S3:

```json
{
  "ts": "2025-10-07T12:31:00.000Z",
  "temp_c": 22.5,
  "temp_f": 72.5,
  "humidity": 45.2,
  "pressure": 1013.25,
  "temp_from_humidity": 23.1,
  "temp_from_pressure": 22.8,
  "cpu_temp": 45.0
}
```

### Silver Layer (Enriched Data)
Includes all bronze fields plus calculated metrics:

```json
{
  "ts": "2025-10-07T12:31:00.000Z",
  "temp_f": 72.5,
  "humidity": 45.2,
  "pressure": 1013.25,
  "dew_point_f": 50.2,
  "dew_point_c": 10.1,
  "comfort_index": "comfortable",
  "pressure_trend_3h": -2.5,
  "pressure_trend_6h": -4.2,
  "pressure_trend_label": "falling",
  "daily_temp_min": 68.0,
  "daily_temp_max": 75.0,
  "daily_temp_avg": 71.5
}
```

**S3 Structure:**
```
s3://your-bucket/
  ├── samples/ (Bronze - Raw Data)
  │   ├── 2025-10-07/
  │   │   ├── 2025-10-07T00-31-00Z.json
  │   │   ├── 2025-10-07T01-31-00Z.json
  │   │   └── ...
  │   └── 2025-10-08/
  │       └── ...
  └── silver/ (Silver - Enriched Data)
      ├── 2025-10-07/
      │   ├── 2025-10-07T00-31-00Z.json
      │   └── ...
      └── 2025-10-08/
          └── ...
```

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uv run uvicorn weather.api:app --reload

# Run tests (if available)
uv run pytest

# Generate mock data for testing
python generate_mock_data.py

# Backfill silver layer from bronze data
./quick-backfill.sh  # Interactive menu
# OR
python backfill_silver.py --days 7  # Last 7 days
python backfill_silver.py --days 1 --dry-run  # Preview only
```

See [BACKFILL_GUIDE.md](backend/BACKFILL_GUIDE.md) for detailed backfill documentation.

### Frontend Development

```bash
cd frontend

# Development mode
npm run dev

# Build for production
npm run build

# Run production build
npm start

# Linting
npm run lint
```

## Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |
| `AWS_REGION` | AWS region | `us-west-2` |
| `S3_BUCKET` | S3 bucket name | Required |
| `S3_PREFIX` | S3 prefix for bronze layer | `samples` |
| `S3_SILVER_PREFIX` | S3 prefix for silver layer | `silver` |
| `SAMPLE_INTERVAL_SEC` | Seconds between readings | `900` (15 min) |

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## Deployment

### Backend (Raspberry Pi)

1. Copy deployment scripts to your Raspberry Pi:
   ```bash
   scp -r deploy/ pi@your-pi:/home/pi/weather_app/
   ```

2. Set up systemd service:
   ```bash
   ssh pi@your-pi
   cd weather_app/deploy
   chmod +x enableservice.sh
   ./enableservice.sh
   ```

3. Manage the service:
   ```bash
   sudo systemctl start weather
   sudo systemctl status weather
   sudo systemctl enable weather  # Start on boot
   ```

### Frontend (Vercel)

```bash
cd frontend
npx vercel
```

Or use GitHub integration for automatic deployments.

**Important:** Update CORS settings in `backend/src/weather/api.py` to include your production domain:

```python
allow_origins=["http://localhost:3000", "https://your-domain.vercel.app"]
```

## Monitoring

- **Backend Logs**: `journalctl -u weather -f` (on Raspberry Pi)
- **S3 Objects**: Use `backend/list_s3_objects.py` to view uploaded readings
- **Frontend**: Check browser console for API errors

## Troubleshooting

### Backend Issues

**"Sense HAT not found"**
- On development machines without hardware, the code uses `sense-emu`
- Edit `hat.py` to switch between real hardware and emulator

**"S3 upload error"**
- Verify AWS credentials are correct
- Check S3 bucket permissions (PutObject, GetObject, ListBucket)
- Ensure bucket exists and is in the correct region

**"No readings found in silver layer"**
- The silver layer may not have data yet if you just deployed
- Run backfill to populate: `./quick-backfill.sh`
- Or wait for new readings to be collected (every 15 minutes)

### Frontend Issues

**"Failed to load current conditions"**
- Ensure backend is running on the correct port
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS is configured in backend

**Charts not displaying**
- Ensure historical data exists in S3
- Check browser console for API errors
- Try a shorter time range first (e.g., 1 hour)

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **boto3** - AWS SDK for Python
- **uvicorn** - ASGI server
- **sense-hat** - Raspberry Pi Sense HAT interface

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Shadcn UI** - Component library built on Radix UI
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Charting library
- **date-fns** - Date utilities

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
