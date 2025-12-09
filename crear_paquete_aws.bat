@echo off
set "CURRENT_DIR=%CD%"
set "BUILD_DIR=%TEMP%\jarvis_build_%RANDOM%"

echo ===================================================
echo   CREANDO PAQUETE PARA AWS LAMBDA (VERSION DESBLOQUEADA)
echo ===================================================
echo.
echo ! Detectado error de bloqueo (probablemente OneDrive).
echo ! Construyendo en carpeta temporal para evitar conflictos...
echo.

echo 1. Preparando entorno limpio en %BUILD_DIR%...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"

echo.
echo 2. Descargando librerias...
call pip install -r requirements.txt -t "%BUILD_DIR%" --no-cache-dir

echo.
echo 3. Copiando codigo fuente...
copy lambda_function.py "%BUILD_DIR%\"
copy jarvis_prompt.md "%BUILD_DIR%\"

echo.
echo 4. Comprimiendo archivo ZIP (Paciencia)...
cd /d "%BUILD_DIR%"
powershell -command "Compress-Archive -Path * -DestinationPath '%CURRENT_DIR%\lambda_function.zip' -Force"
cd /d "%CURRENT_DIR%"

echo.
echo 5. Limpiando archivos temporales...
rmdir /s /q "%BUILD_DIR%"

echo.
echo ===================================================
echo   EXITO TOTAL! Archivo creado: lambda_function.zip
echo ===================================================
echo.
echo YA PUEDES SUBIR ESTE ARCHIVO A AWS LAMBDA.
echo.
pause
