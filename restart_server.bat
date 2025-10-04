@echo off
echo Restarting FastAPI Server with updated CORS configuration...

REM Kill existing Python/uvicorn processes (be careful with this in production)
echo Stopping existing server processes...
taskkill /f /im uvicorn.exe 2>nul
taskkill /f /im python.exe /fi "WINDOWTITLE eq uvicorn*" 2>nul

REM Wait a moment for processes to close
timeout /t 2 /nobreak >nul

echo Starting FastAPI server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause