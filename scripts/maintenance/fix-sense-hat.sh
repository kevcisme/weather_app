#!/bin/bash
# Fix Sense HAT access in virtual environment
# Run this ON YOUR RASPBERRY PI

echo "🔧 Fixing Sense HAT Virtual Environment Access"
echo "=============================================="
echo ""

cd ~/apps/weather_app/backend

echo "1️⃣  Recreating virtual environment with system site packages..."
rm -rf .venv
uv venv --system-site-packages
uv sync

echo ""
echo "2️⃣  Testing Sense HAT access in virtual environment..."
if uv run python -c "from sense_hat import SenseHat; s = SenseHat(); print(f'✅ Success! Temp: {s.get_temperature():.1f}°C, Humidity: {s.get_humidity():.1f}%')" 2>/dev/null; then
    echo "Sense HAT is now accessible!"
else
    echo "⚠️  Still having issues. Trying alternative method..."
    
    # Alternative: manually link system packages
    VENV_PATH=".venv/lib/python$(python3 --version | grep -oP '\d+\.\d+')/site-packages"
    SYSTEM_PATH="/usr/lib/python3/dist-packages"
    
    echo "Linking system Sense HAT packages..."
    ln -sf $SYSTEM_PATH/sense_hat* $VENV_PATH/ 2>/dev/null
    ln -sf $SYSTEM_PATH/RTIMU* $VENV_PATH/ 2>/dev/null
    ln -sf $SYSTEM_PATH/RTIMULib* $VENV_PATH/ 2>/dev/null
    
    # Test again
    uv run python -c "from sense_hat import SenseHat; s = SenseHat(); print(f'✅ Success! Temp: {s.get_temperature():.1f}°C')"
fi

echo ""
echo "3️⃣  Restarting weather service..."
sudo systemctl restart weather.service

echo ""
echo "4️⃣  Waiting for service to start..."
sleep 5

echo ""
echo "5️⃣  Testing API endpoint..."
if curl -s http://localhost:8000/latest | grep -q "temp_c"; then
    echo "✅ API is now returning data!"
    echo ""
    echo "Current reading:"
    curl -s http://localhost:8000/latest | python3 -m json.tool
else
    echo "⚠️  API still returning empty data"
    echo ""
    echo "Check logs with:"
    echo "  journalctl -u weather.service -n 50"
fi

echo ""
echo "✅ Done!"
echo ""
