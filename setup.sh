#!/bin/bash

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Run Gunicorn
echo "Running Gunicorn..."
gunicorn --bind=0.0.0.0:5000 --workers=4 app:app &

# Add more commands as needed
