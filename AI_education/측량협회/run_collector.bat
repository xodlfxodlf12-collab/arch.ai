@echo off
chcp 65001 > nul
setlocal

:: 스크립트 위치로 이동 (상대 경로 보장)
cd /d "%~dp0"

echo [*] 공간정보산업협회 측량업체 데이터 수집을 시작합니다...
python collect_survey_companies.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 데이터 수집 중 오류가 발생했습니다.
) else (
    echo.
    echo [OK] 데이터 수집이 성공적으로 완료되었습니다.
)

pause
