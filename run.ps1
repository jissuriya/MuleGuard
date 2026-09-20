# MuleGuard Launcher
Write-Host "[MuleGuard] Launching Dashboard..." -ForegroundColor Cyan

if (Get-Command streamlit -ErrorAction SilentlyContinue) {
    streamlit run app.py
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    python -m streamlit run app.py
} else {
    & "C:\Users\jissu\AppData\Local\Programs\Python\Python314\python.exe" -m streamlit run app.py
}
