@echo off
title PDFS Agent - 종료
echo PDFS 에이전트를 종료합니다...

taskkill /f /fi "WINDOWTITLE eq PDFS Agent" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq PDFS Agent" >nul 2>&1

echo 종료 완료.
timeout /t 2 >nul
