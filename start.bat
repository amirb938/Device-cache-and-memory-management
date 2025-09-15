@echo off
echo Starting Cache Management Web Panel...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
)

REM Install requirements if needed
echo Installing/Updating requirements...
venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo Starting web server...
echo The web interface will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Start the application
venv\Scripts\python.exe run.py

pause
