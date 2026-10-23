@echo off
chcp 65001 > nul
title محمل الفيديوهات CLI - Video Downloader

SET PYTHON_PATH="C:\Users\Desig\AppData\Local\Python\bin\python.exe"

IF EXIST %PYTHON_PATH% (
    %PYTHON_PATH% cli.py
) ELSE (
    python cli.py
)

pause
