#!/bin/bash

set -e

if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

if [ ! -f "backend/.env" ]; then
    echo "Warning: backend/.env file not found"
    echo "Please create it from .env.example and add your AlphaGenome API key"
    exit 1
fi

cleanup() {
    echo ""
    echo "Shutting down..."
    [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
    [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Starting Backend..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run:"
    echo "cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

python main.py &
BACKEND_PID=$!
cd ..

echo "Backend started (PID: $BACKEND_PID)"
echo "API: http://localhost:8000"
echo ""

echo "Starting Frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
cd ..

echo "Frontend started (PID: $FRONTEND_PID)"
echo "App: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo ""

wait $BACKEND_PID
wait $FRONTEND_PID
