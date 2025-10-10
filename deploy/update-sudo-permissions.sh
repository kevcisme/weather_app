#!/usr/bin/env bash
# Update sudo permissions for GitHub Actions runner
set -euo pipefail

echo "🔐 Updating Sudo Permissions for GitHub Runner"
echo "=============================================="
echo ""

# Create sudoers file with all needed permissions
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

echo "✅ Sudo permissions updated successfully!"
echo ""
echo "Permissions granted:"
echo "  - systemctl restart weather.service"
echo "  - systemctl restart weather-frontend.service"
echo "  - systemctl status weather.service"
echo "  - systemctl status weather-frontend.service"
echo "  - journalctl -u weather.service"
echo "  - journalctl -u weather-frontend.service"
echo ""

