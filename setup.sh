#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

echo "Creating virtual environment..."
python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }

echo "Installing dependencies..."
venv/bin/pip install -r requirements.txt || { echo "Failed to install dependencies"; exit 1; }

echo "Activating virtual environment..."
source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

echo "Running setup..."
python setup.py || { echo "Setup failed"; deactivate; exit 1; }

echo "Deactivating environment..."
deactivate || { echo "Failed to deactivate virtual environment"; exit 1; }
