# API Connection Fix Documentation

## Problem Summary

The frontend was not properly calling the backend due to mismatches between:
1. Frontend API URL configuration
2. Backend CORS settings
3. Nginx proxy configuration
4. Development vs Production environment handling

## Issues Fixed

### 1. Frontend API Client (`frontend/src/lib/api.ts`)

**Problem:** Frontend was always calling `http://localhost:8000` directly, even in production.

**Solution:** Added smart auto-detection:
- **Development** (localhost): Calls `http://localhost:8000` directly
- **Production** (deployed on Pi): Uses `/api/` path which nginx proxies to backend
- Can be overridden via `NEXT_PUBLIC_API_URL` environment variable

### 2. Backend CORS Configuration (`backend/src/weather/api.py`)

**Problem:** CORS only allowed `localhost:3000`, blocking production access.

**Solution:** Updated to allow all origins (`*`) since backend is behind nginx in production. This is safe because:
- Production traffic goes through nginx (port 80)
- Backend is not directly exposed
- nginx handles security

### 3. Environment Configuration

**Created:**
- `frontend/.env.example` - Template for local development
- `frontend/.env.production.local` - Production environment (empty API_URL = auto-detect)
- `frontend/.env.local` - Local development (points to localhost:8000)

### 4. Deployment Scripts

**Updated:** `scripts/deploy/rsync_deploy.sh` and `scripts/deploy/rsync_deploy_configurable.sh`

**Changes:**
- Exclude `.env.local` from deployment (don't copy dev config to production)
- Auto-create `.env.production.local` on Pi during deployment
- Exclude `__pycache__` from backend deployment
- Updated access URLs to show nginx (port 80) as primary

## How It Works Now

### Development Mode (Local Mac)
```
Browser → http://localhost:8000 → FastAPI Backend (direct)
Browser → http://localhost:3000 → Next.js Frontend
```

### Production Mode (Raspberry Pi)
```
Browser → http://192.168.86.49:80 → Nginx
                                      ├─→ / → Next.js (port 3000)
                                      └─→ /api/ → FastAPI (port 8000)
```

### Frontend API Detection Logic
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || (
  typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? '/api'  // Production: use nginx proxy
    : 'http://localhost:8000'  // Development: direct connection
);
```

## Testing

### Local Development
1. Start backend: `cd backend && uv run uvicorn weather.api:app --reload --host 0.0.0.0 --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Access: `http://localhost:3000`
4. Frontend should call: `http://localhost:8000/latest` and `http://localhost:8000/history`

### Production (Raspberry Pi)
1. Deploy: `./scripts/deploy/rsync_deploy.sh`
2. Access: `http://192.168.86.49`
3. Frontend should call: `/api/latest` and `/api/history` (proxied by nginx to port 8000)

## Verification

Check browser developer console:
- Network tab should show API calls
- In development: calls to `localhost:8000`
- In production: calls to `/api/` endpoints
- No CORS errors

Check backend logs:
```bash
# On Raspberry Pi
sudo journalctl -u weather.service -f
```

Check frontend logs:
```bash
# On Raspberry Pi
sudo journalctl -u weather-frontend.service -f
```

## Environment Variables Summary

| Environment | NEXT_PUBLIC_API_URL | Result |
|------------|---------------------|--------|
| Local Dev | `http://localhost:8000` | Direct to backend |
| Production | (empty) | Auto-detect → `/api/` |
| Custom | `http://custom-host:port` | Use custom URL |

## Next Steps

1. **Test locally** - Make sure `http://localhost:3000` works
2. **Deploy to Pi** - Run `./scripts/deploy/rsync_deploy.sh`
3. **Test production** - Check `http://192.168.86.49`
4. **Monitor logs** - Use `journalctl` to check for errors

## Troubleshooting

### Frontend can't connect to backend
- Check if backend is running: `curl http://localhost:8000/latest`
- Check frontend API URL in browser console
- Check CORS errors in browser console

### Production nginx not working
- Check nginx config: `sudo nginx -t`
- Check nginx status: `sudo systemctl status nginx`
- Check nginx logs: `sudo journalctl -u nginx -f`

### Backend not responding
- Check service status: `sudo systemctl status weather.service`
- Check logs: `sudo journalctl -u weather.service -f`
- Check if port 8000 is listening: `sudo netstat -tulpn | grep 8000`

