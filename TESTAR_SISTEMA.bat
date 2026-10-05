@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\activate.bat (
  echo Rode INSTALAR.bat primeiro.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python -m compileall -q .
if errorlevel 1 (
  echo ERRO: teste de sintaxe falhou.
  pause
  exit /b 1
)
python -c "from core.ai import fallback_package; p=fallback_package('teste','Feminino'); assert len(p['affirmations'])==60; print('Teste interno OK')"
where ffmpeg >nul 2>nul && echo FFmpeg OK || echo FFmpeg nao encontrado
where ollama >nul 2>nul && echo Ollama instalado || echo Ollama opcional ainda nao instalado
echo.
echo Testes concluidos.
pause
