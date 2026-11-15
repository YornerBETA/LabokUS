@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (echo Install Python 3.10+ x64: https://www.python.org/downloads/windows/ & pause & exit /b 1)
py -3 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo Dependencies installed. This is not a signed MSI/EXE installer.
pause
exit /b 0
:fail
echo Installation failed.
pause
exit /b 1