@echo off
echo 🧬 GenomeCostTracker Demo Startup
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Generate demo data
echo.
echo 📊 Generating demo data...
cd /d "%~dp0"
python demo-data-generator.py

REM Start backend server
echo.
echo 🚀 Starting FastAPI backend...
cd /d "%~dp0..\backend"

REM Install Python dependencies if needed
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Start backend in background
start "GenomeCost Backend" cmd /k "uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend server
echo.
echo 🎨 Starting Angular frontend...
cd /d "%~dp0..\frontend"

REM Install Node dependencies if needed
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
)

REM Start frontend
start "GenomeCost Frontend" cmd /k "ng serve --host 0.0.0.0 --port 4200"

REM Wait for frontend to start
echo Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo.
echo 🎉 GenomeCostTracker Demo is starting up!
echo ========================================
echo.
echo 🌐 Frontend: http://localhost:4200
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 🔑 Demo Login Credentials:
echo    Email: demo@genomecost.com
echo    Password: demo123
echo.
echo 📊 The demo includes:
echo    • 75 sample genomics jobs
echo    • 45 days of cost trend data
echo    • Budget alerts and recommendations
echo    • Real-time cost monitoring
echo.
echo Press any key to open the application in your browser...
pause >nul

REM Open browser
start http://localhost:4200

echo.
echo 🚀 GenomeCostTracker Demo is now running!
echo.
echo To stop the demo:
echo 1. Close this window
echo 2. Close the backend and frontend terminal windows
echo 3. Or run: scripts\stop-demo.bat
echo.
pause