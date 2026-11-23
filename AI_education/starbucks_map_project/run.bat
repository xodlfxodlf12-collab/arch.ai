@echo off
title 스타벅스 매장 지도 시각화 프로젝트
echo ======================================================
echo    스타벅스 데이터 수집 및 지도 시각화 실행기
echo ======================================================
echo.
echo [1/2] 스타벅스 매장 데이터 수집 중 (crawler.py)...
python crawler.py
echo.
echo [2/2] 인터랙티브 지도 생성 중 (visualize_map.py)...
python visualize_map.py
echo.
echo ======================================================
echo  완료! 브라우저에서 map.html 지도를 엽니다.
echo ======================================================
start map.html
pause
