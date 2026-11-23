@echo off
chcp 65001 > nul
setlocal

:: 스크립트 위치로 이동 (상대 경로 보장)
cd /d "%~dp0"

echo [*] 전국 측량업체 공간정보 지도를 브라우저로 실행합니다...
start survey_map_osm.html

echo [OK] 웹 브라우저에서 지도가 정상 실행되었습니다.
echo.
pause
