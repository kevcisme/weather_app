# Development Guide

This guide explains how to develop the weather app locally while connecting to the Raspberry Pi backend.

## Architecture Overview

- **Backend**: FastAPI application running on Raspberry Pi (port 8000)
- **Frontend**: Next.js application that can run locally or on the Pi (port 3000)
- **Data Storage**: AWS S3 for weather readings

## Development Setup

### Option 1: Frontend on Mac, Backend on Pi (Recommended for Development)

This is the recommended setup for frontend development. Your Raspberry Pi continues to collect real weather data while you develop the UI locally.

1. **Ensure your Pi backend is running:**
   ```bash
   # SSH into your Pi
   ./deploy/quick-ssh.sh
   
   # Check backend status
   sudo systemctl status weather
   ```

2. **Configure frontend to use Pi backend:**
   
   The frontend is already configured via `.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://192.168.86.49:8000
   ```

3. **Start frontend development server:**
   ```bash
   # Easy way - uses the convenience script
   ./dev-frontend-with-pi.sh
   
   # Or manually
   cd frontend
   npm run dev
   ```

4. **Access the app:**
   - Open http://localhost:3000 in your browser
   - The frontend will call the Pi backend for real weather data

### Option 2: Both Frontend and Backend Locally

If you want to run everything locally (useful for testing without the Pi):

1. **Set up Python backend locally:**
   ```bash
   cd backend
   uv sync
   source backendenv.sh  # Sets up AWS credentials
   uv run uvicorn weather.api:app --host 0.0.0.0 --port 8000
   ```

2. **Configure frontend for localhost:**
   ```bash
   cd frontend
   # Edit .env.local or remove it to use default localhost:8000
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

3. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

### Option 3: Production Setup (Both on Pi)

This is how it runs in production with nginx as a reverse proxy.

See [DEPLOYMENT.md](./DEPLOYMENT.md) for details.

## Environment Variables

### Frontend (`frontend/.env.local`)

- `NEXT_PUBLIC_API_URL`: Backend API URL
  - Dev with Pi: `http://192.168.86.49:8000`
  - Dev locally: `http://localhost:8000`
  - Production: Leave empty (uses nginx proxy at `/api`)

### Backend (`backend/backendenv.sh`)

- AWS credentials for S3 access
- See `backend/backendenv.sh` (not committed to git)

## Troubleshooting

### Can't reach Pi backend

1. **Check if Pi is on network:**
   ```bash
   ping 192.168.86.49
   ```

2. **Check if backend is running:**
   ```bash
   curl http://192.168.86.49:8000/latest
   ```

3. **SSH into Pi and check service:**
   ```bash
   ./deploy/quick-ssh.sh
   sudo systemctl status weather
   sudo journalctl -u weather -f  # View logs
   ```

### CORS issues

The backend is configured to allow all origins (`allow_origins=["*"]`), so CORS shouldn't be an issue. If you see CORS errors:

1. Check that the backend is running
2. Verify the URL in `.env.local` is correct
3. Check browser console for specific error messages

### Frontend not picking up environment changes

1. Stop the dev server (Ctrl+C)
2. Delete `.next` folder: `rm -rf frontend/.next`
3. Restart: `npm run dev`

## API Endpoints

The backend exposes these endpoints:

- `GET /latest` - Most recent reading from S3
- `GET /current` - Real-time reading from sensor
- `GET /history?hours=N` - Historical data (1-168 hours)

## Development Tips

1. **Hot Reload**: Next.js dev server has hot reload enabled. Changes to React components will reflect immediately.

2. **API Changes**: If you modify the backend API, you may need to update:
   - `frontend/src/lib/api.ts` (API client)
   - TypeScript interfaces for data types

3. **Real Data**: When connected to the Pi, you're working with real sensor data. Perfect for testing!

4. **Network Requirements**: Your Mac and Pi must be on the same local network for this setup to work.

## Next Steps

- See [DEPLOYMENT.md](./DEPLOYMENT.md) for deploying changes to the Pi
- See [README.md](./README.md) for project overview
- See [FRONTEND_SETUP.md](./FRONTEND_SETUP.md) for frontend details

