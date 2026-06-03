@echo off
REM ============================================================
REM  Sistema de Validacion de Seguros Vehiculares
REM  Ejecutar con doble clic desde la carpeta raiz del proyecto
REM ============================================================

title Sistema de Seguros Vehiculares

echo ============================================================
echo   Sistema de Validacion de Seguros Vehiculares
echo   Fasecolda v2.0  ^|  Validaciones v3.0
echo ============================================================
echo.

REM Obtener ruta absoluta
set ROOT=%~dp0

REM Liberar puertos si estaban ocupados
echo [1/4] Liberando puertos 8001 y 8002...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001 2^>nul') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002 2^>nul') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul

REM Instalar dependencias
echo [2/4] Instalando dependencias de Fasecolda...
cd /d "%ROOT%fasecolda"
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: Falló la instalacion de dependencias de Fasecolda.
    pause & exit /b 1
)

echo [3/4] Instalando dependencias de Validaciones...
cd /d "%ROOT%validaciones"
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: Falló la instalacion de dependencias de Validaciones.
    pause & exit /b 1
)

REM Arrancar servicios en ventanas independientes
echo [4/4] Iniciando microservicios...

start "Fasecolda v2.0 - Puerto 8001" cmd /k "title Fasecolda v2.0 - Puerto 8001 && cd /d "%ROOT%fasecolda" && python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

timeout /t 4 /nobreak >nul

start "Validaciones v3.0 - Puerto 8002" cmd /k "title Validaciones v3.0 - Puerto 8002 && cd /d "%ROOT%validaciones" && python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload"

timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo  SERVICIOS ACTIVOS:
echo.
echo  Fasecolda    ^> http://localhost:8001/docs
echo  Validaciones ^> http://localhost:8002/docs
echo.
echo  Placas de prueba:
echo    ABC123  ^> APROBADA   (300 pts)
echo    XYZ789  ^> RECHAZADA  (400 pts)
echo    DEF456  ^> APROBADA   (0 pts)
echo    GHI012  ^> RECHAZADA  (700 pts)
echo ============================================================
echo  Cierra las ventanas de cada servicio para detenerlos.
echo ============================================================
pause
