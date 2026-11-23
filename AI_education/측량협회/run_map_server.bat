@echo off
chcp 65001 > nul
setlocal

:: 스크립트 위치로 이동
cd /d "%~dp0"

echo ======================================================
echo    측량업체 공간정보 지도 로컬 웹서버를 시작합니다.
echo    브라우저가 자동으로 열립니다.
echo    (종료하려면 이 창을 닫으시면 됩니다)
echo ======================================================
echo.

:: 1초 후 기본 브라우저 자동 오픈
start "" "http://localhost:8080/survey_map_osm.html"

:: 경량 로컬 웹서버 가동 (보안/CORS 제약 100% 해결)
python -m http.server 8080

pause
