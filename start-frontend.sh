#!/bin/bash

echo "🚀 Starting Code Review Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "📁 Navigating to frontend directory..."
    cd frontend
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting development server on http://localhost:3000"
echo "📡 API will connect to http://localhost:8000"
echo ""
echo "Make sure your Django backend is running on port 8000!"
echo ""

npm start
