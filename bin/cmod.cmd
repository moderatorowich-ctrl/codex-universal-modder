@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0cmod.ps1" %*
exit /b %errorlevel%
