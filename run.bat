@echo off
REM Helper script for Windows to work with the PDF Renamer

if "%1"=="" goto run
if /i "%1"=="run" goto run
if /i "%1"=="test" goto test
if /i "%1"=="bash" goto bash
if /i "%1"=="build" goto build
if /i "%1"=="help" goto help
if /i "%1"=="logs" goto logs

echo Unknown command: %1
echo.
goto help

:run
docker-compose run --rm pdfnameforger
exit /b 0

:test
docker-compose run --rm -it pdfnameforger python /app/scripts/test_patterns.py
exit /b 0

:bash
docker-compose run --rm -it pdfnameforger bash
exit /b 0

:build
docker-compose build
exit /b 0

:logs
docker-compose logs -f
exit /b 0

:help
echo PDF Renamer Docker Helper
echo.
echo Usage: run.bat [command]
echo.
echo Commands:
echo   run              Run the PDF renamer (main.py)
echo   test             Test regex patterns interactively
echo   bash             Start interactive bash shell
echo   build            Build Docker image
echo   logs             Show container logs
echo   help             Show this help message
exit /b 0
