@echo off
cd /d "%~dp0..\.."
title Obi Shorts Queue
rem Renders several shot lists back to back without stopping. Edit the list below to change the queue.
for %%S in (obi_shorts\obi_rain_rescue.md obi_shorts\obi_farm_parade.md obi_shorts\obi_morning_chores.md) do (
    echo.
    echo ==================== %%S ====================
    call "%~dp0render_shots.bat" "%%S" nopause
)
echo.
echo [*] All videos done. They are in obi_shorts\final
start "" "obi_shorts\final"
pause
