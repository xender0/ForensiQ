@echo off
echo Starting local web server for ForensiQ Report Viewer...
echo.
echo Open your browser and go to: http://localhost:8000/index.html
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
python -m http.server 8000

