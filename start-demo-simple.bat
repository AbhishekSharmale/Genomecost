@echo off
echo Starting GenomeCostTracker Demo...

REM Start backend
echo Starting backend server...
cd /d "%~dp0backend"
start "Backend" cmd /k "py -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start frontend (if Angular is available)
echo Starting frontend...
cd /d "%~dp0frontend"
if exist "node_modules" (
    start "Frontend" cmd /k "npx ng serve --host 0.0.0.0 --port 4200"
) else (
    echo Installing Angular dependencies...
    npm install
    start "Frontend" cmd /k "npx ng serve --host 0.0.0.0 --port 4200"
)

echo.
echo Demo is starting up!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:4200
echo API Docs: http://localhost:8000/docs
echo.
echo Demo Login: demo@genomecost.com / demo123
pause