@echo off
REM Genera JuegoDeLaVida.exe (sin consola, con icono). Requiere PyInstaller.
cd /d "%~dp0"
set "PYDIR=.venv\Scripts"
if not exist "%PYDIR%\pyinstaller.exe" set "PYDIR=..\.venv_face\Scripts"
if not exist "%PYDIR%\pyinstaller.exe" (
  echo Falta PyInstaller:  "%PYDIR%\python.exe" -m pip install pyinstaller
  pause & exit /b 1
)
"%PYDIR%\pyinstaller.exe" --noconfirm --clean --windowed --onedir ^
  --name "JuegoDeLaVida" --icon "recursos\icono.ico" ^
  vida.py
echo.
echo Listo: dist\JuegoDeLaVida\JuegoDeLaVida.exe
pause
