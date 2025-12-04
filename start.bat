@echo off
REM Quick Start Script for CryptoBot Dashboard - Windows
REM This script sets up and runs the dashboard locally

echo ========================================
echo    CryptoBot Dashboard - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if virtual environment exists
if not exist "venv_new\" (
    echo Creating virtual environment...
    python -m venv venv_new
)

REM Activate virtual environment
echo Activating virtual environment...
call venv_new\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    if exist ".env.example" (
        echo Copying .env.example to .env...
        copy .env.example .env
        echo.
        echo Please edit .env file and add your API keys.
        echo Then run this script again.
        pause
        exit /b 0
    ) else (
        echo ERROR: .env.example not found
        echo Please create a .env file manually
        pause
        exit /b 1
    )
)

REM Check if API keys are configured
findstr /C:"your_binance_api_key" .env >nul
if not errorlevel 1 (
    echo WARNING: API keys not configured in .env file!
    echo The app will run but API calls will fail.
    echo Please edit .env and add your Binance API keys.
    echo.
    choice /C YN /M "Continue anyway"
    if errorlevel 2 exit /b 0
)

REM Create necessary directories
echo Creating necessary directories...
if not exist "logs\" mkdir logs
if not exist "backups\" mkdir backups
if not exist "data\" mkdir data

REM Run the dashboard
echo.
echo ========================================
echo   Starting CryptoBot Dashboard...
echo   Access at: http://localhost:8501
echo   Press Ctrl+C to stop
echo ========================================
echo.

streamlit run src\dashboard\flynt_style_dashboard.py
