@echo off
chcp 65001 >nul
set "PROJ_DIR=C:\Projects\InfluencerMonitoring"
cd /d "%PROJ_DIR%"

:: Check if the python process with InfluencerMonitoring.py is running
wmic process where "name='python.exe' or name='pythonw.exe'" get commandline 2>nul | find /I "InfluencerMonitoring.py" >nul

if %ERRORLEVEL% equ 0 (
    echo [INFO] InfluencerMonitoring is already running. Skipping startup.
    timeout /t 3 >nul
    exit /b 0
) else (
    echo [INFO] InfluencerMonitoring is not running. Starting it now...
    :: Use python.exe to run with a visible console window
    start "Influencer Monitor" "%PROJ_DIR%\venv\Scripts\python.exe" "%PROJ_DIR%\InfluencerMonitoring.py"
    exit /b 0
)
