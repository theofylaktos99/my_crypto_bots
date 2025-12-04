@echo off
REM start_advanced.bat - Quick start script for Advanced Dashboard (Windows)

echo ==================================================
echo 🚀 CryptoBot Professional - Advanced Dashboard
echo ==================================================
echo.
echo Starting advanced features dashboard...
echo.
echo Available modules:
echo   📊 Market Overview
echo   🎯 Advanced Strategies (Fibonacci, ML)
echo   📈 Portfolio Optimizer
echo   📉 Strategy Comparison
echo   🤖 ML Predictions
echo   📐 Fibonacci Analysis
echo   ⚙️ Risk Management
echo.
echo ==================================================
echo.

REM Check if streamlit is installed
streamlit --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit is not installed!
    echo Install it with: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Launch advanced dashboard
streamlit run src/dashboard/advanced_dashboard.py

echo.
echo Dashboard closed. Thank you for using CryptoBot Professional! 💎
pause
