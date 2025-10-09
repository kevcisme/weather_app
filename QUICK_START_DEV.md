# Quick Start: Local Frontend Development

## TL;DR - Start Developing Now

```bash
# From the project root
./dev-frontend-with-pi.sh
```

Then open http://localhost:3000 in your browser!

## What This Does

✅ Runs the Next.js frontend on your Mac (port 3000)  
✅ Connects to your Raspberry Pi backend (192.168.86.49:8000)  
✅ Shows real weather data from your actual sensor  
✅ Supports hot reload - changes appear instantly  

## How It Works

1. **Frontend Configuration**: The `.env.local` file tells Next.js to use your Pi's backend:
   ```
   NEXT_PUBLIC_API_URL=http://192.168.86.49:8000
   ```

2. **CORS**: Already configured on the backend to allow cross-origin requests

3. **API Client**: `frontend/src/lib/api.ts` reads the environment variable and makes requests to your Pi

## Available API Endpoints

Your Pi backend exposes:

- **GET /latest** - Most recent weather reading from S3
- **GET /current** - Real-time sensor reading (live!)
- **GET /history?hours=24** - Historical data (1-168 hours)

Test them directly:
```bash
curl http://192.168.86.49:8000/latest
curl http://192.168.86.49:8000/current
curl http://192.168.86.49:8000/history?hours=24
```

## Project Structure

```
weather_app/
├── frontend/              # Next.js app (TypeScript/React)
│   ├── src/
│   │   ├── app/          # Pages (page.tsx, layout.tsx)
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities & API client
│   ├── .env.local        # Your local config (git-ignored)
│   └── .env.example      # Template for .env.local
│
└── backend/              # FastAPI app (Python)
    └── src/weather/      # Weather collection & API
```

## Troubleshooting

### "Cannot reach backend"

```bash
# Check if Pi is on network
ping 192.168.86.49

# Check if backend responds
curl http://192.168.86.49:8000/latest

# SSH into Pi and check service
./deploy/quick-ssh.sh
sudo systemctl status weather
```

### Changes not showing up?

1. Stop dev server (Ctrl+C)
2. Clear Next.js cache: `rm -rf frontend/.next`
3. Restart: `./dev-frontend-with-pi.sh`

### Want to use a local backend instead?

```bash
# Edit frontend/.env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local

# Start local backend (in a separate terminal)
cd backend
uv run uvicorn weather.api:app --host 0.0.0.0 --port 8000

# Start frontend
cd frontend
npm run dev
```

## Next Steps

- **Make UI changes**: Edit files in `frontend/src/`
- **View backend logs**: `./deploy/quick-ssh.sh` then `sudo journalctl -u weather -f`
- **Deploy changes**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Full dev guide**: See [DEVELOPMENT.md](./DEVELOPMENT.md)

## Pro Tips

1. **Keep Pi running**: Your backend collects data 24/7, so keep it running even while developing
2. **Real data = better testing**: You're testing with actual sensor data, not mocks!
3. **Network required**: Your Mac and Pi must be on the same network
4. **Browser DevTools**: Use React DevTools and Network tab for debugging

---

**Happy coding!** 🌤️ Your weather station is live at http://localhost:3000

