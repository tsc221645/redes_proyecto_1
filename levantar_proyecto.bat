@echo off
setlocal

rem Executive Insights - launcher local para Windows
rem SQL Anywhere debe estar levantado previamente.

set "PROJECT_ROOT=%~dp0"

if not exist "%PROJECT_ROOT%.env" (
    echo [ERROR] Falta el archivo .env en la raiz del proyecto.
    echo         Copia .env.example a .env y completa sus valores.
    pause
    exit /b 1
)

echo SQL Anywhere debe estar levantado previamente.

start "Executive Insights - API" cmd /k "cd /d "%PROJECT_ROOT%" && conda run --no-capture-output -n dm1 python -m uvicorn backend.api.app:app --reload"
start "Executive Insights - Frontend" cmd /k "cd /d "%PROJECT_ROOT%frontend" && npm.cmd run dev"

echo.
echo Servicios iniciados en terminales separadas:
echo   API:      http://127.0.0.1:8000
echo   Frontend: http://localhost:5173
echo   API docs: http://127.0.0.1:8000/docs
echo.
echo El servidor MCP de negocio se inicia automaticamente junto con la API.
pause
endlocal
