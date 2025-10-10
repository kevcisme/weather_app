#!/usr/bin/env bash
# Configure and install GitHub Actions runner as a service
set -euo pipefail

echo "🔧 GitHub Actions Runner Configuration"
echo "======================================="
echo ""

# Check if token is provided
if [ $# -eq 0 ]; then
    echo "❌ Error: GitHub token required"
    echo ""
    echo "Usage: $0 <GITHUB_TOKEN> [REPO_URL]"
    echo ""
    echo "Example:"
    echo "  $0 YOUR_GITHUB_TOKEN"
    echo "  $0 YOUR_GITHUB_TOKEN https://github.com/username/weather_app"
    echo ""
    echo "To get a token:"
    echo "  1. Go to your GitHub repository"
    echo "  2. Settings → Actions → Runners"
    echo "  3. Click 'New self-hosted runner'"
    echo "  4. Copy the token from the configuration command"
    echo ""
    exit 1
fi

TOKEN=$1
REPO_URL=${2:-"https://github.com/YOUR_USERNAME/weather_app"}

# Prompt for repo URL if not provided
if [[ $REPO_URL == *"YOUR_USERNAME"* ]]; then
    echo "📝 Enter your GitHub repository URL"
    echo "   (e.g., https://github.com/username/weather_app):"
    read -r REPO_URL
fi

RUNNER_DIR="$HOME/actions-runner"

if [ ! -d "$RUNNER_DIR" ]; then
    echo "❌ Error: Runner directory not found at $RUNNER_DIR"
    echo "   Please run setup-github-runner.sh first"
    exit 1
fi

cd "$RUNNER_DIR"

# Check if already configured
if [ -f ".runner" ]; then
    echo "⚠️  Runner is already configured"
    read -p "Remove existing configuration and reconfigure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing configuration..."
        ./config.sh remove --token "$TOKEN"
    else
        echo "Exiting..."
        exit 0
    fi
fi

echo "⚙️  Configuring runner..."
echo "   Repository: $REPO_URL"
echo ""

# Configure the runner
./config.sh --url "$REPO_URL" --token "$TOKEN" --name "pi-weather-station" --work "_work" --labels "raspberry-pi,self-hosted,weather-app"

echo ""
echo "✅ Runner configured successfully!"
echo ""

# Set up sudo permissions for systemctl and journalctl
echo "🔐 Setting up sudo permissions for service management..."

# Create sudoers file with multiple commands
sudo tee /etc/sudoers.d/github-runner > /dev/null << EOF
# GitHub Actions runner permissions
$USER ALL=(ALL) NOPASSWD: /bin/systemctl restart weather.service
$USER ALL=(ALL) NOPASSWD: /bin/systemctl restart weather-frontend.service
$USER ALL=(ALL) NOPASSWD: /bin/systemctl status weather.service
$USER ALL=(ALL) NOPASSWD: /bin/systemctl status weather-frontend.service
$USER ALL=(ALL) NOPASSWD: /bin/journalctl -u weather.service *
$USER ALL=(ALL) NOPASSWD: /bin/journalctl -u weather-frontend.service *
EOF

sudo chmod 0440 /etc/sudoers.d/github-runner
echo "✅ Sudo permissions configured"

echo ""
echo "📦 Installing runner as a service..."
sudo ./svc.sh install

echo ""
echo "🚀 Starting runner service..."
sudo ./svc.sh start

echo ""
echo "⏳ Waiting for service to start..."
sleep 3

echo ""
echo "📊 Runner status:"
sudo ./svc.sh status

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your GitHub Actions runner is now running on this Pi!"
echo ""
echo "Commands:"
echo "  Status:  sudo ~/actions-runner/svc.sh status"
echo "  Stop:    sudo ~/actions-runner/svc.sh stop"
echo "  Start:   sudo ~/actions-runner/svc.sh start"
echo "  Restart: sudo ~/actions-runner/svc.sh stop && sudo ~/actions-runner/svc.sh start"
echo ""
echo "Next: Create a GitHub Actions workflow file in your repository"
echo "      (.github/workflows/deploy.yml)"
echo ""

