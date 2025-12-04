# Guida Configurazione GitHub (Cloud)

Segui questi passaggi per attivare l'aggiornamento automatico 24/7.

## 1. Crea la Repository su GitHub
1.  Vai su [github.com](https://github.com) e fai login.
2.  Clicca su **New Repository** (o il tasto `+` in alto a destra).
3.  Nome: `spotify-house-goat` (o quello che vuoi).
4.  Imposta su **Private** (Importante! Contiene le tue chiavi).
5.  Clicca **Create repository**.

## 2. Carica i File
Apri il terminale nella cartella del progetto (`c:\Users\andre\Desktop\spotifyapp`) ed esegui questi comandi uno alla volta:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/TUO_NOME_UTENTE/spotify-house-goat.git
git push -u origin main
```
*(Sostituisci `TUO_NOME_UTENTE` con il tuo username GitHub)*

## 3. Imposta i Segreti (Secrets)
Vai nella pagina della tua repository su GitHub:
1.  Clicca su **Settings** (in alto).
2.  Nel menu a sinistra, clicca **Secrets and variables** -> **Actions**.
3.  Clicca **New repository secret**.

Aggiungi questi 4 segreti (copia i valori dal tuo file `.env` e dalla chat):

| Nome | Valore |
| :--- | :--- |
| `SPOTIPY_CLIENT_ID` | (Prendilo dal file `.env`) |
| `SPOTIPY_CLIENT_SECRET` | (Prendilo dal file `.env`) |
| `SPOTIPY_REDIRECT_URI` | `http://127.0.0.1:8888/callback` |
| `SPOTIFY_CACHE` | **(Copia il codice lungo che ti ho mandato in chat)** |

## 4. Verifica
1.  Vai nella tab **Actions** su GitHub.
2.  Dovresti vedere "Update Spotify Playlist".
3.  Puoi cliccarci e fare "Run workflow" per testarlo subito, oppure aspettare la prossima ora.
