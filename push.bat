@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo [*] Starting GitHub Upload (git push)...
git push -u origin main

echo.
echo [*] Done.
pause
