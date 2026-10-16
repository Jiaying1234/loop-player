@echo off
setlocal

cd /d "%~dp0"
set "PYTHON=%~dp0venv\Scripts\python.exe"
set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"

if not exist "%PYTHON%" (
    echo Could not find the project Python environment:
    echo %PYTHON%
    pause
    exit /b 1
)

if not exist "%CHROME%" (
    set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
)

if not exist "%CHROME%" (
    set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"
)

if not exist "%CHROME%" (
    echo Could not find Google Chrome.
    pause
    exit /b 1
)

echo Starting Loop Player...
set "LOOP_PLAYER_CHROME=%CHROME%"
"%PYTHON%" "%~dp0app.py"

endlocal
