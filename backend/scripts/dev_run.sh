#!/bin/bash
# Development server run script

set -e

# Change to backend directory
cd "$(dirname "$0")/.."

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Create uploads directory
mkdir -p uploads

# Run the development server
echo "Starting Receipts API development server..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
