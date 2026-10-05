@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Instalador - Modo Protagonista Studio

echo.
echo ================================================
echo   MODO PROTAGONISTA STUDIO - INSTALACAO LOCAL
echo ================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [ERRO] Python nao foi encontrado.
  echo Instale Python 3.11 ou 3.12 em https://www.python.org/downloads/
  echo Marque a opcao "Add python.exe to PATH" durante a instalacao.
  pause
  exit /b 1
)

if not exist .venv\Scripts\python.exe (
  echo [1/5] Criando ambiente virtual...
  python -m venv .venv
  if errorlevel 1 goto :fail
) else (
  echo [1/5] Ambiente virtual ja existe.
)

call .venv\Scripts\activate.bat

echo [2/5] Atualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 goto :fail

echo [3/5] Instalando dependencias Python...
pip install -r requirements.txt
if errorlevel 1 goto :fail

echo [4/5] Verificando FFmpeg...
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg nao encontrado.
  where winget >nul 2>nul
  if not errorlevel 1 (
    choice /M "Deseja tentar instalar o FFmpeg gratuitamente pelo winget agora"
    if not errorlevel 2 (
      winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
      echo Feche e abra o Prompt de Comando depois da instalacao para atualizar o PATH.
    )
  ) else (
    echo Instale manualmente o FFmpeg e adicione-o ao PATH.
  )
) else (
  echo FFmpeg encontrado.
)

echo [5/5] Verificando Ollama opcional...
where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama ainda nao esta instalado. O Studio funciona em modo basico sem IA.
  echo Para IA local gratuita, instale em https://ollama.com/download
  echo Depois rode: ollama pull qwen3:4b
) else (
  echo Ollama encontrado.
  echo Se ainda nao tiver o modelo, rode: ollama pull qwen3:4b
)

echo.
echo ================================================
echo Instalacao concluida.
echo Agora execute ABRIR_MODO_PROTAGONISTA.bat
echo ================================================
pause
exit /b 0

:fail
echo.
echo [ERRO] A instalacao nao terminou corretamente.
echo Copie a mensagem acima e envie para o ChatGPT revisar.
pause
exit /b 1
