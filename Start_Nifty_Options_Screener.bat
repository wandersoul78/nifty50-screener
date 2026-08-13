@echo off
title Nifty Options Open=Low & Open=High Screener
color 0A
echo =======================================================
echo  Starting Standalone Nifty Options OHL Screener...
echo =======================================================
python nifty_options_ohl_screener.py
echo.
echo Press any key to exit...
pause > nul
