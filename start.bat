@echo off
REM Hand Hygiene Compliance System - Startup Script (Windows)
REM Starts both backend (Flask) and frontend (React) servers

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo Hand Hygiene Compliance Monitoring System
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

REM Check Node.js
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Node.js^/npm is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Start Backend
echo [1/3] Starting Backend Server...
cd /d "%SCRIPT_DIR%backend"
start "Hand Hygiene Backend" cmd /k python app.py
if %errorlevel% neq 0 (
    echo Failed to start backend
    pause
    exit /b 1
)
echo OK - Backend started

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start Frontend
echo [2/3] Starting Frontend Server...
cd /d "%SCRIPT_DIR%frontend"
start "Hand Hygiene Frontend" cmd /k npm run dev
if %errorlevel% neq 0 (
    echo Failed to start frontend
    pause
    exit /b 1
)
echo OK - Frontend started

REM Print summary
echo.
echo ==========================================
echo OK - System Started Successfully
echo ==========================================
echo.
echo Backend API:  http://localhost:5000
echo Frontend:     http://localhost:5173
echo.
echo Open http://localhost:5173 in your browser
echo.
echo To populate with mock data, run:
echo   python scripts\populate_mock_data.py
echo.
echo Close the backend and frontend windows to stop the servers
echo.
pause
