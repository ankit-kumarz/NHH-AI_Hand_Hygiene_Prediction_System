#!/bin/bash

# Hand Hygiene Compliance System - Startup Script
# Starts both backend (Flask) and frontend (React) servers

set -e

echo "=========================================="
echo "Hand Hygiene Compliance Monitoring System"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running on Windows (Git Bash, WSL, etc.)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    WINDOWS=1
fi

# Backend startup
echo -e "${BLUE}[1/3]${NC} Starting Backend Server..."
cd "$(dirname "$0")/backend"

# Check if Python exists
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "✗ Python is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Use python3 or python depending on what's available
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Start Flask backend in background
$PYTHON_CMD app.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Wait a moment for backend to start
sleep 2

# Frontend startup
echo -e "${BLUE}[2/3]${NC} Starting Frontend Server..."
cd "$(dirname "$0")/frontend"

# Check if Node.js exists
if ! command -v npm &> /dev/null; then
    echo "✗ Node.js/npm is not installed. Please install Node.js 16+ first."
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Start React frontend in background
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

# Print access information
echo ""
echo "=========================================="
echo -e "${GREEN}✓ System Started Successfully${NC}"
echo "=========================================="
echo ""
echo "📊 Backend API:  http://localhost:5000"
echo "🎨 Frontend:     http://localhost:5173"
echo "📱 Open http://localhost:5173 in your browser"
echo ""
echo "To populate with mock data, run:"
echo "  python scripts/populate_mock_data.py"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Trap Ctrl+C and kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Servers stopped.'" INT TERM

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
