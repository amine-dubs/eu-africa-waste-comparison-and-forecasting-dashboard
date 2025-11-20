@echo off
REM Waste Management Dashboard - Quick Launcher
REM Double-click this file to start the dashboard

echo ========================================
echo   WASTE MANAGEMENT DASHBOARD
echo   Starting Streamlit...
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo ERROR: app.py not found!
    echo Please run this script from the DataVisTp1 folder.
    pause
    exit /b 1
)

REM Start the dashboard
echo Dashboard is starting...
echo.
echo The browser will open automatically.
echo.
echo To stop the dashboard, close this window or press Ctrl+C
echo.

streamlit run app.py

pause
