@echo off
REM EDCopilot Chit Chat Updater - Windows Batch File
REM This file provides easy execution of the content updater

echo ========================================
echo   EDCopilot Chit Chat Updater
echo   Automated Content Generation
echo ========================================
echo.

REM Check if Python is available
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    echo.
    echo Try running: py --version
    pause
    exit /b 1
)

echo Python found, using py command

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Please copy env.example to .env and configure your settings
    echo.
    pause
    exit /b 1
)

REM Run the updater
echo Starting EDCopilot Chit Chat Updater...
echo.

py src/main.py %*

echo.
echo ========================================
echo   Update process completed
echo ========================================
echo.

REM Check if we should start EDCopilot after update
for /f "tokens=2 delims==" %%a in ('findstr "START_EDCOPILOT_AFTER_UPDATE" .env 2^>nul') do set START_EDCOPILOT=%%a
for /f "tokens=2 delims==" %%a in ('findstr "DIR_EDCOPILOT" .env 2^>nul') do set DIR_EDCOPILOT=%%a

if /i "%START_EDCOPILOT%"=="TRUE" (
    if defined DIR_EDCOPILOT (
        if exist "%DIR_EDCOPILOT%\LaunchEDCoPilot.exe" (
            echo Starting EDCopilot...
            start "" "%DIR_EDCOPILOT%\LaunchEDCoPilot.exe"
        ) else (
            echo WARNING: LaunchEDCoPilot.exe not found in %DIR_EDCOPILOT%
            echo Please check the DIR_EDCOPILOT variable in .env
            pause
        )
    ) else (
        echo WARNING: DIR_EDCOPILOT not set in .env file
        pause
    )
)

REM All operations completed, pause and exit
exit /b 0
