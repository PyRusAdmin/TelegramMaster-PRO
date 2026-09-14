@echo off
chcp 65001 > nul
python setup.py
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Ошибка при установке зависимостей.
)
pause