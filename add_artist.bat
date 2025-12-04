@echo off
set /p artist="Inserisci il nome dell'artista da aggiungere: "
python manager.py add "%artist%"
pause
