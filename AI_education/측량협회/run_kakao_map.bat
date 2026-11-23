@echo off
chcp 65001 > nul
setlocal

:: 스크립트 위치로 이동
cd /d "%~dp0"

echo ======================================================
echo    측량업체 공간정보 [카카오 지도]를 시작합니다.
echo    웹 브라우저가 자동으로 열립니다.
echo ======================================================
echo.

:: 1초 후 기본 브라우저 자동 오픈
start "" "http://localhost:8080/survey_map_kakao.html"

:: 로컬 웹서버 실행 (카카오 지도 도메인 인증용)
python -m http.server 8080

pause
