#!/bin/bash
# Quick setup script for the frontend

set -e

echo "🌤️  Weather Station Frontend Setup"
echo "=================================="
echo ""

# Check if .env.local exists
if [ ! -f "frontend/.env.local" ]; then
    echo "📝 Creating .env.local file..."
    cat > frontend/.env.local << EOF
# Backend API URL
# For local development, point to backend on localhost
# For production (on Pi), leave empty to use /api/ path (nginx proxy)
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    echo "✅ Created frontend/.env.local"
    echo ""
    echo "ℹ️  Local development will use: http://localhost:8000"
    echo "ℹ️  Production deployment will use: /api/ (nginx proxy)"
else
    echo "✅ frontend/.env.local already exists"
fi

echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "To start the development server:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "To build for production:"
echo "  cd frontend"
echo "  npm run build"
echo "  npm start"
echo ""
