@echo off
setlocal
set OUT=%USERPROFILE%\\Desktop\\Kolobok-PC-diagnostics.txt
(
 echo Kolobok PC diagnostics
 echo Date: %DATE% %TIME%
 echo.
 echo ==== Windows ====
 ver
 systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type" /C:"Total Physical Memory" /C:"Available Physical Memory" /C:"Processor(s)"
 echo.
 echo ==== Python ====
 py -0p 2^>nul
 python --version 2^>nul
 echo.
 echo ==== Display ====
 dxdiag /t "%TEMP%\\kolobok-dxdiag.txt" ^>nul 2^>nul
 timeout /t 3 ^>nul
 if exist "%TEMP%\\kolobok-dxdiag.txt" findstr /I /C:"Card name" /C:"Dedicated Memory" /C:"Display Memory" /C:"Driver Version" "%TEMP%\\kolobok-dxdiag.txt"
) > "%OUT%"
echo Report saved to %OUT%
echo Review the report before sharing; it may contain device details.
start notepad "%OUT%"