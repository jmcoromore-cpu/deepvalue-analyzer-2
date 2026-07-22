@echo off
REM ============================================================
REM   DeepValue Analyzer - cerrar la app
REM   Cierra las ventanas del backend y el frontend.
REM ============================================================

echo Cerrando DeepValue Analyzer...

REM Cierra las ventanas por su titulo
taskkill /FI "WINDOWTITLE eq DeepValue - BACKEND*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq DeepValue - FRONTEND*" /T /F >nul 2>&1

echo Hecho. Puedes cerrar esta ventana.
timeout /t 3 /nobreak >nul
