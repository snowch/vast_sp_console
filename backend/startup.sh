#!/bin/bash
# start.sh - Development startup script

set -e

echo "Starting VAST Services Python Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your VAST configuration"
fi

# Start the application
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 3001 --reload

