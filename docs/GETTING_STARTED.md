# Getting Started with Weather Station

This guide will help you get your weather station dashboard up and running quickly.

## ⚡ Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# 1. Setup frontend and create .env.local
./scripts/setup/setup-frontend.sh

# 2. Configure backend (one-time setup)
# Create backend/src/weather/.env with your AWS credentials:
cat > backend/src/weather/.env << EOF
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-west-2
S3_BUCKET=your-bucket-name
S3_PREFIX=samples
SAMPLE_INTERVAL_SEC=900
EOF

# 3. Start both services
./scripts/dev/start-dev.sh
```

That's it! Your dashboard will open at http://localhost:3000

### Option 2: Manual Setup

#### Backend
```bash
cd backend

# Create .env file (see above)

# Install and run
uv sync
uv run uvicorn weather.api:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Install and run
npm install
npm run dev
```

## 📊 Dashboard Features

### Current Conditions Panel (Left)
- **Temperature**: Displays in both Fahrenheit and Celsius
- **Humidity**: Percentage relative humidity
- **Barometric Pressure**: In hectopascals (hPa)
- **Auto-refresh**: Updates every 60 seconds

### Historical Data Charts (Right)
Interactive charts showing:
1. **Temperature Trends** - Both °F and °C on dual axes
2. **Humidity Trends** - Percentage over time
3. **Pressure Trends** - Barometric pressure changes

#### Time Range Options
- 1 hour - Recent detailed view
- 6 hours - Short-term trends
- 12 hours - Half-day overview
- 24 hours (default) - Full day trends
- 48 hours - Two-day comparison
- 3 days - Weather pattern recognition
- 7 days - Weekly overview

## 🔧 Configuration

### Backend API Endpoint
Default: `http://localhost:8000`

To change, edit `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://your-backend-host:8000
```

**Important**: Restart the frontend after changing this value.

### CORS Settings
If deploying the frontend to a different domain, update `backend/src/weather/api.py`:

```python
allow_origins=[
    "http://localhost:3000",
    "https://your-domain.com"  # Add your domain
]
```

### Sampling Interval
Default: 900 seconds (15 minutes)

To change, edit `backend/src/weather/.env`:
```bash
SAMPLE_INTERVAL_SEC=300  # 5 minutes
```

## 🐛 Troubleshooting

### "Failed to load current conditions"
**Causes:**
- Backend not running
- Wrong API URL in `.env.local`
- CORS not configured

**Solutions:**
1. Check backend is running: `curl http://localhost:8000/latest`
2. Verify `.env.local` has correct URL
3. Check browser console for detailed errors

### Charts show "No historical data available"
**Causes:**
- No data in S3 yet (wait 15 minutes for first upload)
- S3 permissions issue
- Wrong time range selected

**Solutions:**
1. Check S3 bucket: `cd backend && python list_s3_objects.py`
2. Try shorter time range (1 hour)
3. Verify AWS credentials in backend `.env`

### Backend won't start
**Common Issues:**
- Missing dependencies: Run `uv sync` in backend directory
- Invalid AWS credentials: Check backend `.env` file
- Port 8000 in use: Change port or kill conflicting process

### Frontend build errors
**Solutions:**
1. Delete `node_modules` and reinstall: 
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```
2. Clear Next.js cache: `rm -rf .next`
3. Check Node version: Requires Node 18+

## 📱 Mobile Access

The dashboard is fully responsive and works great on mobile devices:

1. Find your computer's local IP: `ifconfig` (Mac/Linux) or `ipconfig` (Windows)
2. Access from mobile: `http://192.168.x.x:3000`

**Note**: Mobile device must be on the same network.

## 🚀 Production Deployment

### Frontend (Vercel)
```bash
cd frontend
npx vercel --prod
```

### Backend (Raspberry Pi)
```bash
# Copy to Pi
scp -r deploy/ pi@your-pi:/home/pi/weather_app/

# On Pi, set up systemd service
ssh pi@your-pi
cd weather_app/deploy
./scripts/setup/enableservice.sh
sudo systemctl enable weather
sudo systemctl start weather
```

## 📊 Data Storage

### S3 Structure
```
s3://your-bucket/samples/
  └── 2025-10-07/
      ├── 2025-10-07T00-31-00Z.json
      ├── 2025-10-07T01-31-00Z.json
      └── ...
```

### Sample Reading
```json
{
  "ts": "2025-10-07T12:31:00.000Z",
  "temp_c": 22.5,
  "temp_f": 72.5,
  "humidity": 45.2,
  "pressure": 1013.25
}
```

## 💡 Tips & Best Practices

1. **First Run**: Wait at least 15 minutes for initial data to appear
2. **Optimal Sampling**: 15 minutes (900s) balances data quality and API costs
3. **S3 Costs**: ~$0.01/month for typical usage (1 reading every 15 min)
4. **Data Retention**: No automatic cleanup - implement lifecycle policy if needed
5. **Monitoring**: Use `journalctl -u weather -f` on Raspberry Pi to watch logs

## 🔗 Useful Commands

```bash
# Backend logs (Raspberry Pi)
journalctl -u weather -f

# List S3 objects
cd backend && python list_s3_objects.py

# Generate mock data for testing
cd backend && python generate_mock_data.py

# Check API health
curl http://localhost:8000/latest

# Frontend production build
cd frontend && npm run build

# View build size
cd frontend && npm run build -- --profile
```

## 📚 Learn More

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **Shadcn UI**: https://ui.shadcn.com
- **Recharts**: https://recharts.org

## 🤝 Need Help?

Check out the main [README.md](README.md) for architecture details and full documentation.
