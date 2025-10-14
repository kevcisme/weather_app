#!/usr/bin/env bash
# First-time deployment script
# Use this for initial setup, then use rsync_deploy.sh for updates

set -euo pipefail
RSPI=pi@192.168.86.49

echo "🌤️  Weather Station - First Time Deployment"
echo "==========================================="
echo ""
echo "This script will:"
echo "  1. Deploy files to your Pi at ${RSPI}"
echo "  2. Guide you through running the setup"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "📦 Step 1: Deploying files to Pi..."
echo ""

echo "Deploying backend..."
rsync -az --delete --exclude 'node_modules' --exclude '.next' backend/ $RSPI:~/apps/weather_app/backend/

echo "Deploying frontend..."
rsync -az --delete --exclude 'node_modules' --exclude '.next' frontend/ $RSPI:~/apps/weather_app/frontend/

echo "Deploying scripts..."
rsync -az --delete scripts/ $RSPI:~/apps/weather_app/scripts/

echo ""
echo "✅ Files deployed successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Step 2: Setup on Raspberry Pi"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Now you need to SSH into your Pi and run the setup script."
echo ""
echo "Run these commands:"
echo ""
echo "  ssh ${RSPI}"
echo "  cd ~/apps/weather_app"
echo "  ./scripts/setup/setup-pi.sh"
echo ""
echo "The setup script will:"
echo "  • Install uv (Python package manager)"
echo "  • Install Node.js and npm"
echo "  • Install Python dependencies"
echo "  • Build the frontend"
echo "  • Set up systemd services"
echo "  • Start everything"
echo ""
echo "After setup completes, you can use ./deploy/rsync_deploy.sh for future updates."
echo ""
read -p "Would you like to SSH into the Pi now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔐 SSHing into ${RSPI}..."
    echo "Once connected, run:"
    echo "  cd ~/apps/weather_app && ./scripts/setup/setup-pi.sh"
    echo ""
    ssh $RSPI
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Next Steps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "After running the setup on your Pi:"
echo ""
echo "  1. Access dashboard: http://192.168.86.49:3000"
echo "  2. For updates, use:  ./scripts/deploy/rsync_deploy.sh"
echo ""
