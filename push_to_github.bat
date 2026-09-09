@echo off
echo ======================================================================
echo             Push LANDVAULT AI to GitHub Repository
echo       https://github.com/udaykiranreddydasaram/LANDVAULT
echo ======================================================================
echo.

set PATH=%LOCALAPPDATA%\Programs\git\cmd;%PATH%
cd /d %~dp0

echo Current Git Status:
git status

echo.
echo Pushing to origin main...
echo (If prompted, log in with your GitHub credentials or Personal Access Token)
git push -u origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo ======================================================================
    echo SUCCESS: Project successfully pushed to GitHub!
    echo Visit: https://github.com/udaykiranreddydasaram/LANDVAULT
    echo ======================================================================
) else (
    echo.
    echo PUSH FAILED. Please make sure:
    echo 1. You have write access to https://github.com/udaykiranreddydasaram/LANDVAULT
    echo 2. You enter your GitHub Personal Access Token if prompted for password.
    echo.
)

pause
