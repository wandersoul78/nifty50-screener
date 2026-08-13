@echo off
title Nifty Options Web Dashboard (Streamlit Port 8502)
cd /d "%~dp0"
echo ===================================================
echo   Starting Nifty Options Web Dashboard (Port 8502)
echo ===================================================
echo.
streamlit run nifty_options_streamlit_app.py --server.port 8502
pause
