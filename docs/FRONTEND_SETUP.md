# Frontend Setup Guide

Quick guide to get your weather dashboard running.

## ✅ Prerequisites

The frontend has already been set up with:
- Next.js 15 with TypeScript
- Shadcn UI components
- Recharts for data visualization
- All dependencies installed

## 🚀 Quick Start

### 1. Development Mode

```bash
cd frontend
npm run dev
```

The dashboard will be available at **http://localhost:3000**

### 2. Configure Backend API

The frontend needs to know where your FastAPI backend is running.

#### Option A: Local Backend (Development)

If running the backend on your Mac:

```bash
# .env.local is already configured for this:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

No changes needed! Just make sure your backend is running:
```bash
cd backend
uv run uvicorn weather.api:app --reload --host 0.0.0.0 --port 8000
```

#### Option B: Raspberry Pi Backend (Production)

Once your Pi is running, update the frontend to point to it:

```bash
cd frontend

# Find your Pi's IP address first (on the Pi, run: hostname -I)

# Then update .env.local with one of these:

# Using hostname (if your network supports mDNS/Bonjour):
echo "NEXT_PUBLIC_API_URL=http://raspi.local:8000" > .env.local

# OR using IP address (more reliable):
echo "NEXT_PUBLIC_API_URL=http://192.168.1.100:8000" > .env.local
```

**Important:** Restart the dev server after changing `.env.local`:
```bash
npm run dev
```

## 🔍 Verification

Once the frontend is running, you should see:

### ✅ Successful Connection
- Current temperature, humidity, and pressure display
- Historical data charts appear
- No error messages

### ❌ Connection Issues

If you see **"Failed to load current conditions"**:

1. **Check backend is running:**
   ```bash
   # Test from your Mac:
   curl http://localhost:8000/latest
   
   # Or test Pi:
   curl http://raspi.local:8000/latest
   ```

2. **Check `.env.local` is correct:**
   ```bash
   cat frontend/.env.local
   ```

3. **Check CORS settings** in `backend/src/weather/api.py`:
   ```python
   allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]
   ```

4. **Check browser console** (F12) for detailed error messages

## 🏗️ Production Build

### Build for Production

```bash
cd frontend
npm run build
```

### Run Production Server

```bash
npm start
```

This serves the optimized production build at http://localhost:3000

## 🌐 Deployment Options

### Option 1: Vercel (Recommended)

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# For production
vercel --prod
```

**Important:** After deploying to Vercel, update your backend CORS:

```python
# In backend/src/weather/api.py
allow_origins=[
    "http://localhost:3000",
    "https://your-app.vercel.app"  # Add your Vercel domain
]
```

### Option 2: Self-Hosted

```bash
# Build the app
cd frontend
npm run build

# Copy build to server
scp -r .next package.json package-lock.json user@server:/path/to/app/

# On server, install and run
npm install --production
npm start
```

## 🎨 Customization

### Change Theme

Edit `src/app/globals.css` to customize colors:

```css
:root {
  --primary: 0 0% 9%;        /* Primary color */
  --chart-1: 12 76% 61%;     /* Temperature chart color */
  --chart-2: 173 58% 39%;    /* Humidity chart color */
  --chart-3: 197 37% 24%;    /* Pressure chart color */
}
```

### Add More Time Ranges

Edit `src/app/page.tsx`:

```tsx
<Select value={hours.toString()} onValueChange={(value) => setHours(parseInt(value))}>
  <SelectContent>
    <SelectItem value="1">1 hour</SelectItem>
    <SelectItem value="24">24 hours</SelectItem>
    <SelectItem value="168">7 days</SelectItem>
    <SelectItem value="336">14 days</SelectItem>  {/* Add new options */}
  </SelectContent>
</Select>
```

### Modify Auto-Refresh Interval

In `src/app/page.tsx`, find:

```tsx
// Refresh every 60 seconds
const interval = setInterval(fetchCurrent, 60000);
```

Change `60000` to your desired interval in milliseconds (e.g., `30000` for 30 seconds).

## 📱 Mobile Access

### Access from Phone/Tablet

1. **Find your computer's IP address:**
   ```bash
   # On Mac:
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # On Windows:
   ipconfig
   ```

2. **On mobile browser, visit:**
   ```
   http://192.168.x.x:3000
   ```

3. **Must be on same WiFi network**

### Make it Work Better on Mobile

The dashboard is already responsive, but you can add to `src/app/layout.tsx`:

```tsx
export const metadata = {
  manifest: '/manifest.json',  // Add PWA support
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
}
```

## 🐛 Troubleshooting

### "Module not found" errors

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Charts not displaying

1. Check browser console (F12) for errors
2. Ensure historical data exists:
   ```bash
   curl http://localhost:8000/history?hours=1
   ```
3. Try a shorter time range (1 hour)

### Slow performance

1. Use production build instead of dev mode:
   ```bash
   npm run build
   npm start
   ```

2. Reduce auto-refresh frequency in `page.tsx`

### Environment variables not updating

```bash
# After changing .env.local, you MUST restart:
# Stop dev server (Ctrl+C)
npm run dev
```

**Note:** Environment variables starting with `NEXT_PUBLIC_` are embedded at build time.

## 🔧 Development Tools

### Type checking

```bash
npm run build  # This includes type checking
```

### Linting

```bash
# Install ESLint if needed
npm install -D eslint

# Run linter
npx next lint
```

### View Production Bundle Size

```bash
npm run build
# Look for the Route table showing bundle sizes
```

## 📊 Features Reference

### Current Conditions Panel
- **Updates**: Every 60 seconds
- **Displays**: Temperature (°F & °C), Humidity (%), Pressure (hPa)
- **Icons**: Color-coded by metric type

### Historical Charts
- **Temperature**: Dual-axis chart (°F and °C)
- **Humidity**: Percentage over time
- **Pressure**: Barometric pressure trends
- **Interactive**: Hover for exact values
- **Time Ranges**: 1 hour to 7 days

### Auto-Refresh
- Current conditions refresh every 60 seconds
- Historical data refreshes when time range changes
- No page reload required

## 🚀 Quick Commands

```bash
# Start development
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Run production build
cd frontend && npm start

# Update API endpoint
cd frontend && echo "NEXT_PUBLIC_API_URL=http://raspi.local:8000" > .env.local

# Clear cache and reinstall
cd frontend && rm -rf .next node_modules && npm install
```

## 🔗 Connecting Everything

### Full Stack Development (Mac)

Terminal 1 - Backend:
```bash
cd backend
uv run uvicorn weather.api:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

Or use the convenience script:
```bash
./scripts/dev/start-dev.sh
```

### Production Setup (Pi + Vercel)

1. **Backend on Raspberry Pi**
   - Follow [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)
   - Service runs automatically on boot

2. **Frontend on Vercel**
   - Deploy with `vercel --prod`
   - Set environment variable in Vercel dashboard:
     - `NEXT_PUBLIC_API_URL` = `http://your-pi-ip:8000`

3. **Update Backend CORS**
   - Add Vercel domain to `allow_origins` in `api.py`

## 📖 More Information

- **Getting Started**: [GETTING_STARTED.md](GETTING_STARTED.md)
- **Raspberry Pi Setup**: [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)
- **Main Documentation**: [README.md](README.md)
- **Frontend Docs**: [frontend/README.md](frontend/README.md)

## 💡 Tips

1. **First time?** Use local backend first to test everything
2. **No data?** Wait 15 minutes for first S3 upload, or use mock data
3. **Deploying?** Remember to update CORS settings
4. **Mobile?** Dashboard is fully responsive
5. **Customizing?** All components are in `src/components/weather/`

---

**Need help?** Open an issue or check the browser console for errors!
