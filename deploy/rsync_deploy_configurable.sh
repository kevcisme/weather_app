#!/usr/bin/env bash
# Configurable deployment script that reads from .pi-config
set -euo pipefail

# Load configuration
if [ -f ../.pi-config ]; then
    source ../.pi-config
    RSPI="${PI_USER}@${PI_HOST}"
    echo "📝 Using Pi configuration: ${RSPI}"
else
    # Fallback to hardcoded value
    RSPI=pi@192.168.86.49
    echo "⚠️  No .pi-config found, using default: ${RSPI}"
fi

echo "📦 Deploying backend..."
rsync -az --delete --exclude 'node_modules' --exclude '.next' backend/ $RSPI:~/apps/weather_app/backend/

echo "📦 Deploying frontend..."
rsync -az --delete --exclude 'node_modules' --exclude '.next' frontend/ $RSPI:~/apps/weather_app/frontend/

echo "📦 Deploying deployment scripts..."
rsync -az --delete deploy/ $RSPI:~/apps/weather_app/deploy/

echo "🔄 Updating dependencies and restarting services..."
ssh $RSPI 'cd ~/apps/weather_app/backend && uv sync && cd ~/apps/weather_app/frontend && npm install && npm run build && sudo systemctl restart weather.service && sudo systemctl restart weather-frontend.service'

echo "✅ Deployment complete!"
echo ""
echo "🌐 Access your dashboard at:"
echo "   http://${PI_HOST}:3000"
echo ""
