#!/bin/bash
# Quick Start Script for CryptoBot Dashboard
# This script sets up and runs the dashboard locally

set -e

echo "🚀 CryptoBot Dashboard - Quick Start"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv_new" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv_new
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv_new/bin/activate || source venv_new/Scripts/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    if [ -f ".env.example" ]; then
        echo "📋 Copying .env.example to .env..."
        cp .env.example .env
        echo "⚠️  Please edit .env file and add your API keys before running the app."
        echo "   Then run this script again."
        exit 0
    else
        echo "❌ .env.example not found. Please create a .env file manually."
        exit 1
    fi
fi

# Check if API keys are configured
if grep -q "your_binance_api_key" .env; then
    echo "⚠️  WARNING: API keys not configured in .env file!"
    echo "   The app will run but API calls will fail."
    echo "   Please edit .env and add your Binance API keys."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs backups data

# Run the dashboard
echo ""
echo "✨ Starting CryptoBot Dashboard..."
echo "   Access at: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""
echo "======================================"
echo ""

streamlit run src/dashboard/flynt_style_dashboard.py
