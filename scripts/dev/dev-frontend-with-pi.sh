#!/usr/bin/env bash
# Start frontend development server connected to Raspberry Pi backend
# This script ensures the frontend calls the Pi backend instead of localhost

set -e

PI_IP="192.168.86.49"
PI_PORT="8000"

echo "🔍 Checking if Raspberry Pi backend is reachable..."
if ! curl -s -o /dev/null -w "%{http_code}" "http://${PI_IP}:${PI_PORT}/latest" > /dev/null 2>&1; then
    echo "⚠️  Warning: Cannot reach backend at http://${PI_IP}:${PI_PORT}"
    echo "   Make sure your Raspberry Pi is running and accessible on your network"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Backend is reachable at http://${PI_IP}:${PI_PORT}"
fi

echo ""
echo "🚀 Starting frontend development server..."
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://${PI_IP}:${PI_PORT}"
echo ""

cd frontend
npm run dev

