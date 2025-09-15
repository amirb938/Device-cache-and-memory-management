#!/bin/bash

echo "Starting Cache Management Web Panel..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
echo "Installing/Updating requirements..."
pip install -r requirements.txt

echo
echo "Starting web server..."
echo "The web interface will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo

# Start the application
python run.py
