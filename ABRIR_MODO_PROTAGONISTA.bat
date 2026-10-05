@echo off
cd /d "%~dp0"
title Modo Protagonista Studio
if not exist .venv\Scripts\activate.bat (
  echo Rode INSTALAR.bat primeiro.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
start "" http://127.0.0.1:8501
streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
