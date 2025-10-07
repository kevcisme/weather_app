#!/bin/bash
# Start both backend and frontend in development mode

set -e

echo "🌤️  Starting Weather Station Development Environment"
echo "==================================================="
echo ""

# Check if backend .env exists
if [ ! -f "backend/src/weather/.env" ]; then
    echo "❌ Backend .env file not found!"
    echo "Please create backend/src/weather/.env with your AWS credentials"
    echo "See README.md for details"
    exit 1
fi

# Check if frontend .env.local exists
if [ ! -f "frontend/.env.local" ]; then
    echo "❌ Frontend .env.local file not found!"
    echo "Run ./setup-frontend.sh first"
    exit 1
fi

# Function to handle cleanup
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill 0
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "🚀 Starting FastAPI backend on port 8000..."
cd backend
uv run uvicorn weather.api:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "⏳ Waiting for backend to start..."
sleep 3

echo "🚀 Starting Next.js frontend on port 3000..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 Backend API:  http://localhost:8000"
echo "🔗 Frontend:     http://localhost:3000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for background processes
wait
