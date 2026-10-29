@echo off
cd /d "%~dp0..\.."
setlocal enabledelayedexpansion
title WanGP Story Episode

if not exist "envs.json" (
    echo [!] No environments data found. Please run install.bat first or add your existing environment with manage.bat if you already have one.
    pause
    exit /b 1
)

echo [*] Fetching active environment...
set "ENV_TYPE="
set "ENV_PATH="

for /f "tokens=1,2,3 delims=|" %%A in ('python setup.py get_env_info 2^>nul') do (
    if "%%A"=="ENV_INFO" (
        set "ENV_TYPE=%%B"
        set "ENV_PATH=%%C"
    )
)

if "!ENV_TYPE!"=="" (
    echo [!] No active environment found.
    echo Please run install.bat first or add your existing environment with manage.bat if you already have one.
    pause
    exit /b 1
)

if "!ENV_TYPE!"=="venv" (
    echo [*] Activating venv: !ENV_PATH!
    call "!ENV_PATH!\Scripts\activate.bat"
) else if "!ENV_TYPE!"=="uv" (
    echo [*] Activating uv: !ENV_PATH!
    call "!ENV_PATH!\Scripts\activate.bat"
) else if "!ENV_TYPE!"=="conda" (
    echo [*] Activating conda: !ENV_PATH!
    set "CONDA_BAT="
    where conda >nul 2>nul
    if !errorlevel! equ 0 set "CONDA_BAT=conda"
    if "!CONDA_BAT!"=="" if exist "%USERPROFILE%\Miniconda3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\Miniconda3\condabin\conda.bat"
    if "!CONDA_BAT!"=="" if exist "%USERPROFILE%\Anaconda3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\Anaconda3\condabin\conda.bat"
    if "!CONDA_BAT!"=="" if exist "C:\ProgramData\Miniconda3\condabin\conda.bat" set "CONDA_BAT=C:\ProgramData\Miniconda3\condabin\conda.bat"
    
    if "!CONDA_BAT!"=="" (
        echo [!] Could not find conda.bat. Please ensure Conda is installed.
        pause
        exit /b 1
    )
    call "!CONDA_BAT!" activate "!ENV_PATH!"
) else if "!ENV_TYPE!"=="none" (
    echo [*] Using system Python ^(No virtual environment^)
) else (
    echo [!] Unknown environment type: !ENV_TYPE!
    pause
    exit /b 1
)


set "SCRIPT=%~1"
if "!SCRIPT!"=="" set "SCRIPT=stories\debt_hunter\ep01_account_opened.md"
for %%F in ("!SCRIPT!") do (
    set "SERIES=%%~dpF"
    set "EPNAME=%%~nF"
)
for /f "tokens=1 delims=_" %%E in ("!EPNAME!") do set "EP=%%E"
if not " --test"=="" set "EP=!EP!_test"

echo [*] Building the batch for !SCRIPT!...
python stories\tools\build_episode.py "!SCRIPT!" --test
if !errorlevel! neq 0 (
    pause
    exit /b 1
)

echo [*] Rendering a 3 beat test: the narrator voice and the first characters...
python wgp.py --process "!SERIES!batches\!EP!.json" --output-dir "!SERIES!output\!EP!"

set "MUSIC="
if exist "!SERIES!music.mp3" set MUSIC=--music "!SERIES!music.mp3"
echo [*] Assembling the video...
python stories\tools\assemble_episode.py "!SCRIPT!" --test !MUSIC!

echo.
echo [*] Done. The video and its captions are in !SERIES!final
start "" "!SERIES!final"
pause
