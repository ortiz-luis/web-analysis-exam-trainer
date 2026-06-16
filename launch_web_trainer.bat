@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating local virtual environment...
    py -m venv .venv
    if errorlevel 1 goto error
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo Launching Web Analysis Exam Trainer...
".venv\Scripts\streamlit.exe" run src/app_streamlit.py
if errorlevel 1 goto error

goto end

:error
echo.
echo An error occurred while launching the trainer.
echo Please read the message above.
pause

:end
endlocal
