#!/bin/bash
# Fix Data Collection Issues
# Fixes both Sense HAT access and SSL certificate issues

set -euo pipefail

# Add uv to PATH
export PATH="$HOME/.local/bin:$PATH"

echo "🔧 Fixing Weather Station Data Collection Issues"
echo "================================================="
echo ""

# Detect which workspace is active
RUNNER_WS="/home/pi/actions-runner/_work/weather_app/weather_app/backend"
APPS_WS="/home/pi/apps/weather_app/backend"

if [ -d "$RUNNER_WS" ] && systemctl is-active weather.service | grep -q "active"; then
    WORKSPACE="$RUNNER_WS"
    echo "📍 Using GitHub Runner workspace: $WORKSPACE"
else
    WORKSPACE="$APPS_WS"
    echo "📍 Using apps workspace: $WORKSPACE"
fi

cd "$WORKSPACE"

echo ""
echo "🔍 Diagnosing issues..."
echo ""

# Issue 1: Check Sense HAT
echo "1️⃣  Checking Sense HAT sensor..."
if ! uv run python -c "from sense_hat import SenseHat; SenseHat().get_temperature()" 2>/dev/null; then
    echo "   ⚠️  Sense HAT not accessible in venv"
    echo "   🔧 Fixing: Recreating venv with system site packages..."
    
    rm -rf .venv
    uv venv --system-site-packages
    uv sync
    
    echo "   ✅ Venv recreated with system packages"
else
    echo "   ✅ Sense HAT accessible"
fi

# Issue 2: Check SSL/CA certificates
echo ""
echo "2️⃣  Checking SSL certificate configuration..."

# Update CA certificates
if ! sudo update-ca-certificates 2>/dev/null; then
    echo "   ⚠️  Could not update CA certificates"
else
    echo "   ✅ CA certificates updated"
fi

# Install/update ca-certificates package
echo "   📦 Ensuring ca-certificates package is up to date..."
sudo apt-get update -qq && sudo apt-get install -y -qq ca-certificates curl 2>/dev/null || true

# Set SSL cert file environment variable for Python
echo "   🔧 Configuring SSL cert path for Python..."
if ! grep -q "SSL_CERT_FILE" /etc/systemd/system/weather.service; then
    echo "   ⚠️  Adding SSL_CERT_FILE to service configuration..."
    sudo sed -i '/\[Service\]/a Environment="SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt"' /etc/systemd/system/weather.service
    sudo sed -i '/\[Service\]/a Environment="REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt"' /etc/systemd/system/weather.service
    sudo systemctl daemon-reload
    echo "   ✅ SSL configuration added to service"
else
    echo "   ✅ SSL configuration already present"
fi

# Issue 3: Test S3 connection
echo ""
echo "3️⃣  Testing S3 connection..."
if uv run python -c "
import boto3
import sys
sys.path.insert(0, 'src')
from weather.settings import settings
try:
    s3 = boto3.client('s3', 
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region)
    s3.head_bucket(Bucket=settings.s3_bucket)
    print('✅ S3 connection successful')
except Exception as e:
    print(f'⚠️  S3 connection failed: {e}')
    sys.exit(1)
" 2>&1; then
    echo "   ✅ S3 accessible"
else
    echo "   ⚠️  S3 connection issues detected"
    echo "      This may resolve after service restart"
fi

echo ""
echo "4️⃣  Restarting weather service..."
sudo systemctl restart weather.service

echo ""
echo "5️⃣  Waiting for service to stabilize..."
sleep 8

echo ""
echo "6️⃣  Testing endpoints..."
echo ""

# Test sensor reading
echo "   📊 Testing direct sensor reading (/current):"
CURRENT=$(curl -s http://localhost:8000/current)
if echo "$CURRENT" | grep -q "temp_c"; then
    echo "      ✅ Sensor working! Data:"
    echo "$CURRENT" | python3 -m json.tool | head -6
else
    echo "      ❌ Sensor error:"
    echo "$CURRENT"
fi

echo ""
echo "   📦 Testing latest S3 reading (/latest):"
LATEST=$(curl -s http://localhost:8000/latest)
if echo "$LATEST" | grep -q "temp_c"; then
    echo "      ✅ S3 data available! Latest reading:"
    echo "$LATEST" | python3 -m json.tool | head -6
else
    echo "      ⚠️  No S3 data yet (this is normal for first run):"
    echo "$LATEST"
    echo ""
    echo "      💡 The service uploads every 15 minutes."
    echo "         Check again in 15 minutes, or check logs:"
    echo "         journalctl -u weather.service -f"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Fix complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo "   1. Monitor logs: journalctl -u weather.service -f"
echo "   2. Wait 15 min for first S3 upload"
echo "   3. Test history: curl http://localhost:8000/history?hours=1"
echo ""

