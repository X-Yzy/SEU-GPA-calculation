@echo off
chcp 65001 >nul
cd /d "%~dp0"
pythonw -B "SEU·绩点计算器.py"
if errorlevel 1 (
    echo Launch failed. Trying the Python launcher...
    pyw -3 -B "SEU·绩点计算器.py"
)
