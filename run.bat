@echo off
chcp 65001 >nul
title Bing Automation Tool v2
cls

echo ================================================================
echo               BING REWARDS AUTOMATION TOOL v2
echo ================================================================
echo.

cd /d "%~dp0"

echo [1/3] Kiem tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python chua duoc cai dat hoac chua duoc them vao PATH!
    echo Vui long cai dat Python va tick chon "Add Python to PATH".
    echo.
    pause
    exit /b
)
echo       - Python da san sang.

echo [2/3] Kiem tra moi truong ao venv...
if not exist "venv\Scripts\python.exe" (
    echo       - Dang khoi tao moi truong ao venv...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Khong the tao moi truong ao venv!
        pause
        exit /b
    )
    echo       - Dang cai dat thu vien requirements.txt...
    venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
    echo       - Moi truong ao venv hop le.
)

REM Kiem tra thu vien da cai du chua
venv\Scripts\python.exe -c "import selenium, webdriver_manager, faker" >nul 2>&1
if errorlevel 1 (
    echo       - Dang cap nhat thu vien con thieu...
    venv\Scripts\python.exe -m pip install -r requirements.txt
)
echo       - Thu vien da san sang.

echo.
echo [3/3] Khoi chay Bing Automation...
echo.
venv\Scripts\python.exe bing_auto.py

echo.
echo ================================================================
echo                     TIEN TRINH HOAN TAT
echo ================================================================
pause
