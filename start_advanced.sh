#!/bin/bash
# start_advanced.sh - Quick start script for Advanced Dashboard

echo "=================================================="
echo "🚀 CryptoBot Professional - Advanced Dashboard"
echo "=================================================="
echo ""
echo "Starting advanced features dashboard..."
echo ""
echo "Available modules:"
echo "  📊 Market Overview"
echo "  🎯 Advanced Strategies (Fibonacci, ML)"
echo "  📈 Portfolio Optimizer"
echo "  📉 Strategy Comparison"
echo "  🤖 ML Predictions"
echo "  📐 Fibonacci Analysis"
echo "  ⚙️ Risk Management"
echo ""
echo "=================================================="
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed!"
    echo "Install it with: pip install -r requirements.txt"
    exit 1
fi

# Launch advanced dashboard
streamlit run src/dashboard/advanced_dashboard.py

echo ""
echo "Dashboard closed. Thank you for using CryptoBot Professional! 💎"
