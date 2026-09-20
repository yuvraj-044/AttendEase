#!/bin/bash

# AttendEase Convenience Run Script for Mac

echo "🚀 Starting AttendEase Development Server..."

# Ensure we are in the right directory
cd "$(dirname "$0")"

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Error: python3 could not be found. Please install Python 3."
    exit
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip3 install -q -r requirements/local.txt

# Run migrations
echo "⚙️  Applying migrations..."
python3 manage.py migrate

# Start server
PORT=${1:-8000}
echo "🌐 Server starting at http://127.0.0.1:$PORT/"
echo "Press Ctrl+C to stop the server."

if ! python3 manage.py runserver $PORT; then
    echo ""
    echo "⚠️  Port $PORT is already in use."
    echo "💡 To fix this, you can:"
    echo "   1. Run on a different port: sh run.sh 8001"
    echo "   2. Kill the existing process: lsof -t -i :$PORT | xargs kill -9"
fi
