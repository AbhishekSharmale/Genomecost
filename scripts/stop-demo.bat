@echo off
echo 🛑 Stopping GenomeCostTracker Demo
echo =================================

REM Kill processes by port
echo Stopping backend server (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo Stopping frontend server (port 4200)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":4200" ^| find "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

REM Kill Node.js and Python processes related to the demo
echo Cleaning up remaining processes...
taskkill /f /im "node.exe" /fi "WINDOWTITLE eq GenomeCost Frontend*" >nul 2>&1
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq GenomeCost Backend*" >nul 2>&1

echo.
echo ✅ GenomeCostTracker Demo stopped successfully!
echo.
echo Thank you for trying GenomeCostTracker! 🧬
echo.
echo For more information:
echo • Documentation: docs/
echo • GitHub: https://github.com/genomecost/tracker
echo • Support: support@genomecost.com
echo.
pause