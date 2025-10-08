#!/bin/bash
# Restart weather services and verify they're running with new code

echo "🔄 Restarting Weather Station Services"
echo "======================================="
echo ""

# Stop services
echo "⏹️  Stopping services..."
sudo systemctl stop weather
sudo systemctl stop weather-frontend

# Wait a moment
sleep 2

# Start services
echo "▶️  Starting services..."
sudo systemctl start weather
sudo systemctl start weather-frontend

# Wait for startup
echo "⏳ Waiting for services to initialize..."
sleep 3

# Check status
echo ""
echo "📊 Service Status:"
echo "-------------------"
echo "Backend:"
sudo systemctl is-active weather && echo "✅ Running" || echo "❌ Not running"
echo ""
echo "Frontend:"
sudo systemctl is-active weather-frontend && echo "✅ Running" || echo "❌ Not running"
echo ""

# Test endpoints
echo "🧪 Testing Endpoints:"
echo "---------------------"

echo "Testing /current..."
curl -s http://localhost:8000/current | head -c 100
echo ""
echo ""

echo "Testing /latest..."
curl -s http://localhost:8000/latest | head -c 100
echo ""
echo ""

echo "Testing /history?hours=1..."
curl -s "http://localhost:8000/history?hours=1" | head -c 150
echo ""
echo ""

echo "✅ Done!"
echo ""
echo "To view live logs, run:"
echo "  sudo journalctl -u weather -f"
