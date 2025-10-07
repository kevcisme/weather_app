#!/bin/bash
# Automated setup script for Raspberry Pi
# Run this on your Raspberry Pi after copying the files

set -e

echo "🌤️  Weather Station Raspberry Pi Setup"
echo "======================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Step 1: Installing system dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-venv sense-hat i2c-tools nodejs npm

echo ""
echo "🔧 Step 2: Installing uv (Python package manager)..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    # Add to bashrc for future sessions
    echo 'source $HOME/.cargo/env' >> ~/.bashrc
else
    echo "✅ uv already installed"
fi

echo ""
echo "📁 Step 3: Setting up project directory..."
mkdir -p ~/apps/weather_app
cd ~/apps/weather_app

echo ""
echo "🔑 Step 4: Checking for .env file..."
if [ ! -f backend/src/weather/.env ]; then
    echo "❌ .env file not found!"
    echo ""
    echo "Please create backend/src/weather/.env with your AWS credentials:"
    echo ""
    cat << 'EOF'
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-west-2
S3_BUCKET=your-bucket-name
S3_PREFIX=samples
SAMPLE_INTERVAL_SEC=900
EOF
    echo ""
    read -p "Create .env file now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "AWS Access Key ID: " aws_key
        read -sp "AWS Secret Access Key: " aws_secret
        echo
        read -p "AWS Region [us-west-2]: " aws_region
        aws_region=${aws_region:-us-west-2}
        read -p "S3 Bucket: " s3_bucket
        read -p "S3 Prefix [samples]: " s3_prefix
        s3_prefix=${s3_prefix:-samples}
        read -p "Sample Interval (seconds) [900]: " interval
        interval=${interval:-900}
        
        mkdir -p backend/src/weather
        cat > backend/src/weather/.env << EOF
AWS_ACCESS_KEY_ID=$aws_key
AWS_SECRET_ACCESS_KEY=$aws_secret
AWS_REGION=$aws_region
S3_BUCKET=$s3_bucket
S3_PREFIX=$s3_prefix
SAMPLE_INTERVAL_SEC=$interval
EOF
        chmod 600 backend/src/weather/.env
        echo "✅ Created .env file"
    else
        echo "❌ Cannot continue without .env file"
        exit 1
    fi
else
    echo "✅ .env file found"
    chmod 600 backend/src/weather/.env
fi

echo ""
echo "📦 Step 5: Installing Python dependencies..."
cd backend
uv sync

echo ""
echo "🧪 Step 6: Testing Sense HAT..."
if python3 -c "from sense_hat import SenseHat; s = SenseHat(); print(f'✅ Temp: {s.get_temperature():.1f}°C, Humidity: {s.get_humidity():.1f}%')" 2>/dev/null; then
    echo "✅ Sense HAT is working!"
else
    echo "⚠️  Warning: Could not access Sense HAT"
    echo "The service will use emulator or mock data"
fi

echo ""
echo "🧪 Step 7: Testing S3 connection..."
cd ~/apps/weather_app/backend
if uv run python test_s3_upload.py; then
    echo "✅ S3 connection successful!"
else
    echo "⚠️  Warning: S3 connection failed"
    echo "Check your AWS credentials in .env file"
fi

echo ""
echo "📝 Step 8: Configuring frontend environment..."
if [ ! -f ~/apps/weather_app/frontend/.env.local ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > ~/apps/weather_app/frontend/.env.local
    echo "✅ Created frontend/.env.local"
else
    echo "✅ frontend/.env.local already exists"
fi

echo ""
echo "📦 Step 9: Installing frontend dependencies..."
cd ~/apps/weather_app/frontend
npm install

echo ""
echo "🏗️  Step 10: Building frontend..."
npm run build

echo ""
echo "⚙️  Step 11: Setting up systemd services..."
sudo cp ~/apps/weather_app/deploy/weather.service /etc/systemd/system/weather.service
sudo cp ~/apps/weather_app/deploy/weather-frontend.service /etc/systemd/system/weather-frontend.service
sudo systemctl daemon-reload
sudo systemctl enable weather.service
sudo systemctl enable weather-frontend.service
sudo systemctl start weather.service
sudo systemctl start weather-frontend.service

echo ""
echo "⏳ Waiting for service to start..."
sleep 3

echo ""
echo "🔍 Step 12: Checking service status..."
echo ""
echo "Backend service:"
if sudo systemctl is-active --quiet weather.service; then
    echo "✅ Backend is running!"
else
    echo "❌ Backend failed to start!"
    echo "Check logs with: journalctl -u weather -n 50"
fi

echo ""
echo "Frontend service:"
if sudo systemctl is-active --quiet weather-frontend.service; then
    echo "✅ Frontend is running!"
else
    echo "❌ Frontend failed to start!"
    echo "Check logs with: journalctl -u weather-frontend -n 50"
fi

echo ""
echo "🧪 Step 13: Testing endpoints..."
sleep 3

echo ""
echo "Testing backend API..."
if curl -s http://localhost:8000/latest > /dev/null; then
    echo "✅ Backend API is responding!"
    echo ""
    echo "Current reading:"
    curl -s http://localhost:8000/latest | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/latest
else
    echo "⚠️  Backend API not responding yet (may take a moment to initialize)"
fi

echo ""
echo "Testing frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is responding!"
else
    echo "⚠️  Frontend not responding yet (may take a moment to initialize)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Your weather station is now running!"
echo ""
echo "🌐 Access your dashboard:"
echo "  • Dashboard:  http://$(hostname -I | awk '{print $1}'):3000"
echo "  • Or:         http://raspi.local:3000"
echo ""
echo "Useful commands:"
echo "  • Check backend:   sudo systemctl status weather"
echo "  • Check frontend:  sudo systemctl status weather-frontend"
echo "  • View logs:       journalctl -u weather -f"
echo "  • Restart all:     sudo systemctl restart weather weather-frontend"
echo ""
echo "Direct API access (if needed):"
echo "  • Latest:  http://$(hostname -I | awk '{print $1}'):8000/latest"
echo "  • History: http://$(hostname -I | awk '{print $1}'):8000/history?hours=24"
echo ""
echo "Data will be uploaded to S3 every $(grep SAMPLE_INTERVAL_SEC ~/apps/weather_app/backend/src/weather/.env 2>/dev/null | cut -d= -f2 || echo '900') seconds"
echo ""
echo "📖 For more information, see RASPBERRY_PI_SETUP.md"
echo ""
