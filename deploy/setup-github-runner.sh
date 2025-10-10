#!/usr/bin/env bash
# Setup GitHub Actions Self-Hosted Runner on Raspberry Pi
set -euo pipefail

echo "🚀 GitHub Actions Self-Hosted Runner Setup"
echo "==========================================="
echo ""

# Check if running on Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create runner directory
RUNNER_DIR="$HOME/actions-runner"
echo "📁 Creating runner directory at $RUNNER_DIR"
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

# Check architecture
ARCH=$(uname -m)
echo "🔍 Detected architecture: $ARCH"

# Set runner version and download URL based on architecture
RUNNER_VERSION="2.311.0"
if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    RUNNER_FILE="actions-runner-linux-arm64-${RUNNER_VERSION}.tar.gz"
    DOWNLOAD_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_FILE}"
elif [ "$ARCH" = "armv7l" ]; then
    RUNNER_FILE="actions-runner-linux-arm-${RUNNER_VERSION}.tar.gz"
    DOWNLOAD_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_FILE}"
else
    echo "❌ Unsupported architecture: $ARCH"
    exit 1
fi

# Download runner if not already present
if [ ! -f "$RUNNER_FILE" ]; then
    echo "⬇️  Downloading GitHub Actions Runner v${RUNNER_VERSION}..."
    curl -o "$RUNNER_FILE" -L "$DOWNLOAD_URL"
else
    echo "✅ Runner archive already downloaded"
fi

# Extract if not already extracted
if [ ! -f "./config.sh" ]; then
    echo "📦 Extracting runner..."
    tar xzf "$RUNNER_FILE"
else
    echo "✅ Runner already extracted"
fi

echo ""
echo "✅ Runner downloaded and extracted successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Get a registration token from GitHub:"
echo "   • Go to your repository on GitHub"
echo "   • Settings → Actions → Runners"
echo "   • Click 'New self-hosted runner'"
echo "   • Copy the token from the configuration command"
echo ""
echo "2. Configure the runner:"
echo "   cd $RUNNER_DIR"
echo "   ./config.sh --url https://github.com/YOUR_USERNAME/weather_app --token YOUR_TOKEN"
echo ""
echo "3. Install as a service (optional but recommended):"
echo "   sudo ./svc.sh install"
echo "   sudo ./svc.sh start"
echo ""
echo "4. Check status:"
echo "   sudo ./svc.sh status"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Runner location: $RUNNER_DIR"
echo ""

