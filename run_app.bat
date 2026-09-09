@echo off
echo ======================================================================
echo             LANDVAULT AI - Smart India Hackathon (SIH26018)
echo         "From Legacy Records to Trusted Digital Land Data"
echo ======================================================================
echo.

set PATH=%LOCALAPPDATA%\Programs\nodejs;%LOCALAPPDATA%\Python\pythoncore-3.14-64\Scripts;%LOCALAPPDATA%\Python\bin;%PATH%
set PYTHONPATH=%~dp0

echo Starting FastAPI Backend on port 8000...
start "LANDVAULT AI Backend" cmd /k "cd /d %~dp0 && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo Starting Vite Frontend on port 5173...
start "LANDVAULT AI Frontend" cmd /k "cd /d %~dp0frontend && npm run dev -- --host 127.0.0.1 --port 5173"

timeout /t 2 /nobreak >nul

echo Opening browser at http://127.0.0.1:5173 ...
start http://127.0.0.1:5173

echo.
echo ======================================================================
echo System is running!
echo Frontend: http://127.0.0.1:5173
echo Backend API Docs: http://127.0.0.1:8000/docs
echo ======================================================================
pause
