# Guida Spotify Playlist Manager

## Come si usa

### 1. Aggiungere Artisti
1. Fai doppio click su **`add_artist.bat`**.
2. Scrivi il nome dell'artista (es. "FISHER", "Jamie Jones") e premi Invio.
   - *Il sistema cercherà di capire chi intendi anche se sbagli qualche lettera.*

### 2. Aggiornare la Playlist (Manuale)
1. Fai doppio click su **`run.bat`**.
2. Il sistema cercherà **Nuove Uscite** (Singoli/Album) degli ultimi 7 giorni.
3. Se non ci sono novità, aggiungerà canzoni famose dell'artista.
4. Le canzoni vecchie (più di 7 giorni) verranno rimosse.

### 3. Aggiornamento Automatico (Consigliato)
Per far sì che il PC aggiorni la playlist da solo ogni giorno:
1. Fai doppio click su **`setup_auto_update.bat`**.
2. Se ti chiede i permessi, clicca Sì.
3. Fatto! Ora ogni mattina alle 10:00 il PC controllerà se ci sono nuove canzoni.
   - *Nota: Il PC deve essere acceso a quell'ora.*

## Note
- **Ordine**: Le canzoni sono ordinate per **Artista -> Album -> Numero Traccia**.
- La playlist si chiama **"My Dynamic Weekly"**.
- Le canzoni non vengono duplicate.
- Per gestire tutto da telefono servirebbe un server sempre acceso, ma con l'aggiornamento automatico sul PC ottieni lo stesso risultato (basta accendere il PC ogni tanto).
