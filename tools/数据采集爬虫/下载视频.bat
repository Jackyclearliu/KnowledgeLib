@echo off
rem ============================================================
rem M3U8 downloader launcher
rem All config and messages live in run_download.py (edit there).
rem ============================================================

cd /d "%~dp0"
python run_download.py

echo.
pause
