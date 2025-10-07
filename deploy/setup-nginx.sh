#!/bin/bash
# Optional: Set up Nginx as a reverse proxy
# This allows you to access everything on port 80 instead of separate ports

set -e

echo "🔧 Setting up Nginx reverse proxy..."
echo ""

# Check if Nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "📦 Installing Nginx..."
    sudo apt update
    sudo apt install -y nginx
fi

# Backup existing default config
if [ -f /etc/nginx/sites-enabled/default ]; then
    echo "📋 Backing up existing Nginx config..."
    sudo cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup
fi

# Copy our config
echo "📝 Installing weather station Nginx config..."
sudo cp ~/apps/weather_app/deploy/nginx-weather.conf /etc/nginx/sites-available/weather

# Disable default site
sudo rm -f /etc/nginx/sites-enabled/default

# Enable our site
sudo ln -sf /etc/nginx/sites-available/weather /etc/nginx/sites-enabled/weather

# Test configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx
echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo "✅ Nginx setup complete!"
echo ""
echo "You can now access your dashboard at:"
echo "  • http://$(hostname -I | awk '{print $1}')"
echo "  • http://raspi.local"
echo ""
echo "API endpoints are available at:"
echo "  • http://$(hostname -I | awk '{print $1}')/api/latest"
echo "  • http://$(hostname -I | awk '{print $1}')/api/history?hours=24"
echo ""
