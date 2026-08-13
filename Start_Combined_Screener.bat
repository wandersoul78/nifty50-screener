@echo off
title Combined Screener Launcher (Port 8503)
cd /d "%~dp0"
echo =========================================================
echo   Starting Combined Stocks, Nifty & Bank Nifty Screener
echo =========================================================
echo.

echo Running initial combined scan in background...
python combined_screener.py

echo.
echo Opening Streamlit Web Dashboard at http://localhost:8503 ...
streamlit run streamlit_app.py --server.port 8503
pause
