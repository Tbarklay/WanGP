@echo off
cd /d "%~dp0.."
setlocal enabledelayedexpansion
title WanGP

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


echo [*] Building a one clip test of Old MacDonald with the farmer and dog...
python kids_videos\build_batch.py old_macdonald --test
if !errorlevel! neq 0 (
    pause
    exit /b 1
)

echo [*] Rendering the test clip. The first time, this also downloads the models (can take a while)...
python wgp.py --process kids_videos\batches\old_macdonald_test.json --output-dir kids_videos\output\test

echo.
echo [*] Done. Open kids_videos\output\test\old_macdonald_long_01.mp4 to check the farmer and dog.
start "" "kids_videos\output\test"
pause
