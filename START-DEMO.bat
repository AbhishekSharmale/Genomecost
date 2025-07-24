@echo off
echo.
echo ========================================
echo   GenomeCostTracker Demo Setup
echo ========================================
echo.

REM Start backend API server
echo [1/3] Starting FastAPI backend server...
cd /d "%~dp0backend"
start "GenomeCost Backend" cmd /k "py -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
echo [2/3] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Open HTML demo
echo [3/3] Opening demo dashboard...
cd /d "%~dp0"
start "" "index.html"

echo.
echo ========================================
echo   Demo is now running!
echo ========================================
echo.
echo Frontend Demo:    file:///%~dp0index.html
echo Backend API:      http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Demo Login Credentials:
echo   Email:    demo@genomecost.com
echo   Password: demo123
echo.
echo Features included:
echo   - Real-time cost monitoring dashboard
echo   - Interactive charts and analytics
echo   - Sample genomics job data
echo   - Cost breakdown by resource type
echo   - Budget alerts and recommendations
echo.
echo To stop the demo:
echo   - Close this window
echo   - Close the backend terminal window
echo.
pause