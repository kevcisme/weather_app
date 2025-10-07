#!/bin/bash
# Run this script ON YOUR RASPBERRY PI to diagnose backend issues

echo "🔍 Weather Station Backend Diagnostics"
echo "======================================"
echo ""

echo "1️⃣  Checking backend service status..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo systemctl status weather.service --no-pager
echo ""

echo "2️⃣  Checking if backend is listening on port 8000..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo netstat -tlnp | grep 8000 || echo "❌ Nothing listening on port 8000"
echo ""

echo "3️⃣  Testing backend API endpoint..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -s http://localhost:8000/latest > /dev/null 2>&1; then
    echo "✅ Backend API is responding!"
    echo ""
    echo "Current data:"
    curl -s http://localhost:8000/latest | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/latest
else
    echo "❌ Backend API is not responding"
fi
echo ""

echo "4️⃣  Recent backend logs (last 30 lines)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
journalctl -u weather.service -n 30 --no-pager
echo ""

echo "5️⃣  Checking backend environment file..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f ~/apps/weather_app/backend/src/weather/.env ]; then
    echo "✅ .env file exists"
    echo "Variables set:"
    grep -E "^[A-Z]" ~/apps/weather_app/backend/src/weather/.env | cut -d= -f1
else
    echo "❌ .env file not found at ~/apps/weather_app/backend/src/weather/.env"
fi
echo ""

echo "6️⃣  Checking Sense HAT..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if python3 -c "from sense_hat import SenseHat; s = SenseHat(); print(f'✅ Temp: {s.get_temperature():.1f}°C')" 2>/dev/null; then
    echo "Sense HAT is working!"
else
    echo "⚠️  Cannot access Sense HAT (will use mock data)"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Quick Fixes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "If backend is not running:"
echo "  sudo systemctl restart weather.service"
echo ""
echo "If it's failing to start:"
echo "  journalctl -u weather.service -n 50"
echo ""
echo "To test manually:"
echo "  cd ~/apps/weather_app/backend"
echo "  uv run uvicorn weather.api:app --host 0.0.0.0 --port 8000"
echo ""
