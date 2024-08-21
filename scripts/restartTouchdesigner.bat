@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM Kill existing TouchDesigner processes
taskkill /IM TouchDesigner.exe /F

REM Wait for the process to terminate completely
timeout /T 5 /NOBREAK

REM Check if a project path was provided
if "%~1"=="" (
    echo No project file specified.
    exit /b 1
)

REM Start a new instance of TouchDesigner with the specified project file
"C:\Program Files\Derivative\TouchDesigner\bin\TouchDesigner.exe" "%~1"

