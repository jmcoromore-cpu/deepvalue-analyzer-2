@echo off
REM ============================================================
REM   DeepValue Analyzer - arranque con doble clic
REM   Arranca backend y frontend y abre la app en el navegador.
REM ============================================================
title DeepValue - Lanzador

REM Situarse en la carpeta de este .bat (raiz del proyecto).
REM Las ventanas hijas heredan esta carpeta, por eso dentro se
REM usan rutas relativas (cd backend / cd frontend): asi los
REM espacios en la ruta no dan problemas.
cd /d "%~dp0"

echo.
echo ============================================================
echo   Iniciando DeepValue Analyzer...
echo.
echo   Se abriran 2 ventanas (BACKEND y FRONTEND).
echo   NO las cierres mientras uses la app.
echo ============================================================
echo.

REM --- 1) Backend: activa el entorno virtual y lanza uvicorn ---
start "DeepValue - BACKEND" cmd /k "cd backend && call .venv\Scripts\activate && uvicorn main:app --reload --port 8000"

REM --- 2) Espera a que el backend arranque ---
timeout /t 6 /nobreak >nul

REM --- 3) Frontend: lanza el servidor de desarrollo ---
start "DeepValue - FRONTEND" cmd /k "cd frontend && npm run dev"

REM --- 4) Espera a que el frontend este listo y abre el navegador ---
timeout /t 10 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo   Listo. La app deberia abrirse en el navegador.
echo   Si no se abre sola, entra manualmente en:  http://localhost:5173
echo.
echo   Para CERRAR: cierra las ventanas BACKEND y FRONTEND
echo   (o usa CERRAR_APP.bat).
echo.
echo   Ya puedes cerrar esta ventana.
timeout /t 4 /nobreak >nul
