@echo off
chcp 65001 > nul
title 텍스트 인터랙티브 생존 게임: 학점 수호 & 칼퇴 챌린지
cd /d "%~dp0"
python main.py
pause
