@echo off
set "TASK_NAME=SpotifyPlaylistAutoUpdate"
set "SCRIPT_PATH=%~dp0run.bat"

echo Creating daily task for Spotify Playlist Update...
echo Script path: %SCRIPT_PATH%

schtasks /create /tn "%TASK_NAME%" /tr "\"%SCRIPT_PATH%\"" /sc hourly /mo 1 /f

if %errorlevel% equ 0 (
    echo Task created successfully! The playlist will update EVERY HOUR.
) else (
    echo Failed to create task. Please run as Administrator.
)
pause
