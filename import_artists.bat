@echo off
echo Incolla qui sotto il link della playlist Spotify da cui vuoi importare gli artisti.
echo (Tasto destro per incollare se CTRL+V non funziona)
set /p url="Link Playlist: "
python manager.py import "%url%"
pause
