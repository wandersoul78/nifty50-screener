@echo off
title Yahoo Stock Screener Launcher (Port 3001)
cd /d "%~dp0"
echo ===================================================
echo     Starting Yahoo Stocks-Only Screener (Port 3001)
echo ===================================================
echo.

echo Running Yahoo stock screener scan in background...
powershell -WindowStyle Hidden -Command "Start-Process python -ArgumentList 'open_high_low_screener.py' -WindowStyle Hidden"

echo Opening Web Dashboard at http://localhost:3001 ...
powershell -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:3001'"

npx vite --port 3001
