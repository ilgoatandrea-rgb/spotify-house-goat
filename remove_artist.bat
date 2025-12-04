@echo off
set /p artist="Inserisci il nome dell'artista da RIMUOVERE: "
python manager.py remove "%artist%"
pause
