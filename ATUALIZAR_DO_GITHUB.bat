@echo off
cd /d "%~dp0"
title Atualizar Modo Protagonista Studio
where git >nul 2>nul
if errorlevel 1 (
  echo Git nao encontrado. Instale o GitHub Desktop ou Git para Windows.
  pause
  exit /b 1
)
git remote -v >nul 2>nul
if errorlevel 1 (
  echo Esta pasta ainda nao esta ligada a um repositorio GitHub.
  pause
  exit /b 1
)
echo Buscando atualizacoes...
git pull --ff-only
if errorlevel 1 (
  echo Nao foi possivel atualizar automaticamente. Abra o GitHub Desktop para revisar.
) else (
  echo Sistema atualizado.
)
pause
