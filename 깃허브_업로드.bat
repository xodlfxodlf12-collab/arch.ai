@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo [*] GitHub 업로드 (git push)를 시작합니다...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo [OK] 업로드가 성공적으로 완료되었습니다!
) else (
    echo [ERROR] 업로드 중 오류가 발생했습니다. 브라우저 인증 또는 토큰을 확인해 주세요.
)

pause
