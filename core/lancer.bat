@echo off
REM ============================================
REM Church Application - Lanceur
REM ============================================

echo.
echo ============================================
echo   Church Application - Demarrage
echo ============================================
echo.

REM Check if executable exists
if exist "%~dp0dist\ChurchApp.exe" (
    echo [OK] Executable trouve
    echo.
    echo Lancement de l'application...
    echo.
    start "" "%~dp0dist\ChurchApp.exe"
) else (
    echo [ERREUR] Executable non trouve !
    echo.
    echo Veuillez d'abord executer: pyinstaller ChurchApp.spec
    echo.
    echo Ou lancer directement avec Python:
    echo   python launcher.py
    echo.
    pause
    
    REM Fallback to Python
    echo.
    echo Tentative avec Python...
    python "%~dp0launcher.py"
)

echo.
echo Application lancee !
echo.
