#!/bin/bash
# Quick status check from your Mac

PI_IP="192.168.86.49"

echo "🌤️  Weather Station Status Check"
echo "================================"
echo ""

# Backend API Test
echo -n "Backend API (port 8000): "
if curl -s --connect-timeout 3 http://${PI_IP}:8000/latest > /dev/null 2>&1; then
    echo "✅ Running"
    DATA=$(curl -s http://${PI_IP}:8000/latest)
    if [ "$DATA" = "{}" ]; then
        echo "   ⚠️  No sensor data yet (check logs)"
    else
        echo "   📊 Receiving data"
    fi
else
    echo "❌ Not responding"
fi

# Frontend Test
echo -n "Frontend (port 3000):    "
if curl -s --connect-timeout 3 http://${PI_IP}:3000 > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

echo ""
echo "🔗 Dashboard: http://${PI_IP}:3000"
echo ""
echo "For detailed status, run:"
echo "  ssh pi@${PI_IP} 'sudo systemctl status weather weather-frontend'"
echo ""
echo "For logs, run:"
echo "  ssh pi@${PI_IP} 'journalctl -u weather -n 50'"
echo ""
