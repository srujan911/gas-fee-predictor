@echo off
echo Starting hourly data collection at %date% %time%
cd /d %~dp0
call venv\Scripts\activate.bat
python scripts\scheduled_data_collector.py
echo Data collection completed with exit code %ERRORLEVEL% at %date% %time%
