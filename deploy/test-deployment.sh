#!/usr/bin/env bash
# Test deployment by making a small change and pushing
set -euo pipefail

echo "🧪 CI/CD Deployment Test"
echo "========================"
echo ""

# Check if we're in the right directory
if [ ! -d ".github/workflows" ]; then
    echo "❌ Error: Must run from repository root"
    exit 1
fi

# Check if we have uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes"
    git status --short
    echo ""
    read -p "Commit these changes? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        read -p "Enter commit message: " commit_msg
        git commit -m "$commit_msg"
    else
        echo "Aborting test. Please commit or stash changes first."
        exit 1
    fi
fi

echo "📊 Current status:"
echo "  Branch: $(git branch --show-current)"
echo "  Last commit: $(git log -1 --oneline)"
echo ""

echo "🚀 This will:"
echo "  1. Create a test commit (update timestamp in CI_CD_SETUP.md)"
echo "  2. Push to origin/main"
echo "  3. Trigger GitHub Actions workflow"
echo ""

read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Add timestamp to CI_CD_SETUP.md
echo "" >> CI_CD_SETUP.md
echo "<!-- Last deployment test: $(date -u +"%Y-%m-%d %H:%M:%S UTC") -->" >> CI_CD_SETUP.md

# Commit and push
git add CI_CD_SETUP.md
git commit -m "Test CI/CD deployment - $(date +%Y%m%d-%H%M%S)"

echo ""
echo "📤 Pushing to GitHub..."
git push origin main

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Test commit pushed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Watch deployment progress:"
echo "   GitHub: https://github.com/kevcisme/weather_app/actions"
echo ""
echo "📋 Or watch on Pi:"
echo "   ssh pi@192.168.86.49 'journalctl -u actions.runner.* -f'"
echo ""

