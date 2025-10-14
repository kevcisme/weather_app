#!/usr/bin/env bash
# Uninstall GitHub Actions runner
set -euo pipefail

echo "🗑️  Uninstalling GitHub Actions Runner"
echo "======================================"
echo ""

RUNNER_DIR="$HOME/actions-runner"

if [ ! -d "$RUNNER_DIR" ]; then
    echo "❌ Runner directory not found at $RUNNER_DIR"
    exit 1
fi

cd "$RUNNER_DIR"

echo "⏹️  Stopping the runner service..."
sudo ./svc.sh stop || echo "Service already stopped"

echo ""
echo "🗑️  Uninstalling the runner service..."
sudo ./svc.sh uninstall || echo "Service already uninstalled"

echo ""
echo "🧹 Removing runner configuration..."
if [ -f ".runner" ]; then
    # Get the token from command line or prompt
    if [ $# -eq 0 ]; then
        echo "⚠️  A GitHub token is required to remove the runner from GitHub."
        echo "   If you don't have a token, you can skip this step and just"
        echo "   remove the runner manually from GitHub Settings → Actions → Runners"
        echo ""
        read -p "Do you have a token to remove the runner? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter your GitHub token: " TOKEN
            ./config.sh remove --token "$TOKEN"
        else
            echo "⏭️  Skipping GitHub removal. Please remove manually from GitHub."
        fi
    else
        TOKEN=$1
        ./config.sh remove --token "$TOKEN"
    fi
else
    echo "✅ Runner was not configured"
fi

echo ""
echo "🧹 Removing sudo permissions..."
sudo rm -f /etc/sudoers.d/github-runner

echo ""
echo "✅ Uninstall complete!"
echo ""
echo "To completely remove the runner directory:"
echo "  rm -rf $RUNNER_DIR"
echo ""

