@echo off
echo [MuleGuard] Starting Dashboard...
where streamlit >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    streamlit run app.py
) else (
    python -m streamlit run app.py
)
pause
