@echo off
setlocal
cd /d "%~dp0"
if exist "dist\Kolobok\Kolobok.exe" (start "" "dist\Kolobok\Kolobok.exe" & exit /b 0)
if exist ".venv\Scripts\pythonw.exe" (start "" ".venv\Scripts\pythonw.exe" app\main.py & exit /b 0)
where py >nul 2>nul
if errorlevel 1 (echo Python 3.10+ x64 required. Run install.bat first. & pause & exit /b 1)
start "" pyw -3 app\main.py