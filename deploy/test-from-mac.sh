#!/bin/bash
# Test backend from your Mac

echo "🧪 Testing Weather Station Backend from Mac"
echo "==========================================="
echo ""

PI_IP="192.168.86.49"

echo "1️⃣  Testing backend API (port 8000)..."
echo ""
if curl -s --connect-timeout 5 http://${PI_IP}:8000/latest > /dev/null 2>&1; then
    echo "✅ Backend API is responding!"
    echo ""
    echo "Current weather data:"
    curl -s http://${PI_IP}:8000/latest | python3 -m json.tool 2>/dev/null || curl -s http://${PI_IP}:8000/latest
    echo ""
else
    echo "❌ Cannot reach backend API at http://${PI_IP}:8000"
    echo ""
    echo "Possible issues:"
    echo "  • Backend service not running on Pi"
    echo "  • Port 8000 blocked by firewall"
    echo "  • Backend crashed or failed to start"
    echo ""
fi

echo ""
echo "2️⃣  Testing frontend (port 3000)..."
echo ""
if curl -s --connect-timeout 5 http://${PI_IP}:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is responding!"
else
    echo "❌ Cannot reach frontend at http://${PI_IP}:3000"
fi

echo ""
echo "3️⃣  Checking what ports are open on Pi..."
echo ""
nmap -p 3000,8000 ${PI_IP} 2>/dev/null || echo "nmap not installed, skipping port scan"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Next Steps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "If backend is not responding, SSH into Pi and run:"
echo "  ssh pi@${PI_IP}"
echo "  cd ~/apps/weather_app"
echo "  ./deploy/check-backend.sh"
echo ""
