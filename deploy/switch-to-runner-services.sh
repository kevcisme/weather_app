#!/usr/bin/env bash
# Switch systemd services to use GitHub runner workspace
set -euo pipefail

echo "🔄 Switching to GitHub Runner Services"
echo "======================================="
echo ""

# Check if running on Pi
if [ ! -d "$HOME/actions-runner" ]; then
    echo "❌ Error: GitHub runner directory not found"
    echo "   Expected: $HOME/actions-runner"
    exit 1
fi

# Stop current services
echo "⏹️  Stopping current services..."
sudo systemctl stop weather.service || true
sudo systemctl stop weather-frontend.service || true

# Copy new service files
echo "📝 Installing new service files..."
sudo cp ~/apps/weather_app/deploy/weather-runner.service /etc/systemd/system/weather.service
sudo cp ~/apps/weather_app/deploy/weather-frontend-runner.service /etc/systemd/system/weather-frontend.service

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable services
echo "✅ Enabling services..."
sudo systemctl enable weather.service
sudo systemctl enable weather-frontend.service

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Services Updated Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  NOTE: Services will NOT start until the first GitHub"
echo "   Actions workflow runs and deploys code to:"
echo "   $HOME/actions-runner/_work/weather_app/weather_app/"
echo ""
echo "To trigger the first deployment:"
echo "  1. Commit and push your workflow files to GitHub"
echo "  2. The runner will automatically deploy"
echo "  3. Services will start with the deployed code"
echo ""

