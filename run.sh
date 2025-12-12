#!/bin/bash
# Run the NSZ to NSP Converter Web GUI

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install requirements if not already installed
pip install -r requirements.txt

# Run the application
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
