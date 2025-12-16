#!/bin/bash

# Quick Food Data Loader
# This script uploads the food training data via curl

API_URL="http://localhost:8000"

echo "=========================================="
echo "  FastText Food Classifier - Quick Load"
echo "=========================================="
echo ""

# Check if API is running
echo "Checking API..."
if ! curl -s "$API_URL/api" > /dev/null 2>&1; then
    echo "❌ API is not running!"
    echo "Please start with: docker-compose up"
    exit 1
fi
echo "✅ API is running"
echo ""

# Check if JSON file exists
if [ ! -f "food_training_data.json" ]; then
    echo "❌ food_training_data.json not found!"
    exit 1
fi

echo "📦 Loading food categories from JSON..."

# Read JSON and create batch array
# Note: This is a simplified version. For full functionality use the Python script.

echo ""
echo "⚠️  For best results, use the Python script:"
echo "   python3 load_food_data.py"
echo ""
echo "Or load manually via the web interface at:"
echo "   http://localhost:8000"
echo ""

# Alternative: Load using the Python script if available
if command -v python3 &> /dev/null; then
    echo "🐍 Python detected. Would you like to use the Python loader? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        python3 load_food_data.py
        exit $?
    fi
fi

echo "Opening web interface..."
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:8000"
elif command -v open &> /dev/null; then
    open "http://localhost:8000"
else
    echo "Open http://localhost:8000 in your browser"
fi
