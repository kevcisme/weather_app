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
                          │   Storage       │
                          └─────────────────┘
```

## Features

### Backend (FastAPI + Python)
- 🌡️ Real-time sensor data collection from Raspberry Pi Sense HAT
- ☁️ Automatic upload to AWS S3 with organized date-based structure
- 📊 RESTful API endpoints for current and historical data
- ⚙️ Configurable sampling intervals
- 🔒 Environment-based configuration

### Frontend (Next.js + TypeScript)
- 📱 Responsive, modern dashboard interface
- 📈 Interactive charts for temperature, humidity, and pressure
- ⏱️ Real-time updates (auto-refresh every 60 seconds)
- 📅 Flexible time range selection (1 hour to 7 days)
- 🎨 Beautiful UI built with Shadcn UI and Tailwind CSS

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

Weather readings are stored as JSON in S3:

```json
{
  "ts": "2025-10-07T12:31:00.000Z",
  "temp_c": 22.5,
  "temp_f": 72.5,
  "humidity": 45.2,
  "pressure": 1013.25
}
```

**S3 Structure:**
```
s3://your-bucket/samples/
  ├── 2025-10-07/
  │   ├── 2025-10-07T00-31-00Z.json
  │   ├── 2025-10-07T01-31-00Z.json
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
```

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
| `S3_PREFIX` | S3 key prefix | `samples` |
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
