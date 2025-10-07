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
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    echo "✅ Created frontend/.env.local"
    echo ""
    echo "⚠️  Please update the API URL if your backend is running on a different host/port"
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
