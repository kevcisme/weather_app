#!/usr/bin/env bash
# Quick script to deploy frontend fix to Raspberry Pi

set -e

PI_HOST="192.168.86.49"
PI_USER="pi"
APP_DIR="apps/weather_app"

echo "🚀 Deploying frontend fix to Raspberry Pi..."
echo ""

# Sync frontend code
echo "📦 Syncing frontend code..."
rsync -az --delete \
  --exclude 'node_modules' \
  --exclude '.next' \
  --exclude '.env.local' \
  frontend/ ${PI_USER}@${PI_HOST}:~/${APP_DIR}/frontend/

# Rebuild and restart on Pi
echo ""
echo "🔨 Building frontend on Pi..."
ssh ${PI_USER}@${PI_HOST} << 'ENDSSH'
cd ~/apps/weather_app/frontend
echo "Installing dependencies..."
npm install
echo "Building production bundle..."
npm run build
echo "Restarting frontend service..."
sudo systemctl restart weather-frontend
echo "Checking service status..."
sleep 2
sudo systemctl status weather-frontend --no-pager -l
ENDSSH

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Test the frontend:"
echo "   http://192.168.86.49:3000"
echo ""
echo "📋 View logs:"
echo "   ssh pi@192.168.86.49 'journalctl -u weather-frontend -f'"

