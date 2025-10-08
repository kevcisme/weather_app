#!/usr/bin/env bash
set -euo pipefail
RSPI=pi@192.168.86.49

echo "📦 Deploying backend..."
rsync -az --delete --exclude 'node_modules' --exclude '.next' backend/ $RSPI:~/apps/weather_app/backend/

echo "📦 Deploying frontend..."
rsync -az --delete --exclude 'node_modules' --exclude '.next' frontend/ $RSPI:~/apps/weather_app/frontend/

echo "📦 Deploying deployment scripts..."
rsync -az --delete deploy/ $RSPI:~/apps/weather_app/deploy/

echo ""
echo "🔄 Updating dependencies and restarting services..."
echo ""

# Check if uv is installed, if not, provide helpful message
if ! ssh $RSPI 'command -v uv &> /dev/null'; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  First-time setup required!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Your Pi needs to be set up first. Run:"
    echo ""
    echo "  ssh ${RSPI}"
    echo "  cd ~/apps/weather_app"
    echo "  ./deploy/setup-pi.sh"
    echo ""
    echo "After setup, you can use this script for updates."
    echo ""
    exit 1
fi

ssh $RSPI 'cd ~/apps/weather_app/backend && uv sync && cd ~/apps/weather_app/frontend && npm install && npm run build && sudo systemctl restart weather.service && sudo systemctl restart weather-frontend.service'

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access your dashboard at:"
echo "   http://192.168.86.49:3000"
echo ""
