@echo off
chcp 65001 > nul
title محمل الفيديوهات - Video Downloader

SET PYTHON_PATH="C:\Users\Desig\AppData\Local\Python\bin\python.exe"

IF EXIST %PYTHON_PATH% (
    %PYTHON_PATH% app.py
) ELSE (
    python app.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo حدث خطأ أثناء تشغيل البرنامج. تأكد من تثبيت Python و yt-dlp.
    pause
)
