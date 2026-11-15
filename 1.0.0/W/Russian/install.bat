@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (echo Install Python 3.10-3.12 from https://www.python.org/downloads/windows/ & pause & exit /b 1)
py -3 -m venv .venv
if errorlevel 1 goto fail
.venv\\Scripts\\python.exe -m pip install --upgrade pip
.venv\\Scripts\\python.exe -m pip install pyinstaller
if errorlevel 1 goto fail
.venv\\Scripts\\pyinstaller.exe --noconfirm --clean --windowed --name Kolobok app\\main.py
if errorlevel 1 goto fail
echo EXE build created under dist. This is a local build step, not a signed MSI installer.
pause
exit /b 0
:fail
echo Build failed. See output above.
pause
exit /b 1