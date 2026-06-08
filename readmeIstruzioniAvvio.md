# 🚀 Istruzioni di avvio — AI Market Predictor

Guida pratica per avviare il progetto e usare gli strumenti già pronti.
Tutti i comandi vanno eseguiti dalla cartella principale del progetto:

```bash
cd /Users/marcofilannino/Desktop/ai_market_predictor
```

---

## ⚡ Avvio rapido (vedere subito i grafici)

```bash
cd /Users/marcofilannino/Desktop/ai_market_predictor
source .venv/bin/activate
python scripts/viz/dashboard.py
```

Poi apri il browser su **http://127.0.0.1:8050**
Per fermare la dashboard: premi **Ctrl + C** nel terminale.

---

## 1. Attivare l'ambiente Python

Prima di lanciare qualsiasi script, attiva il virtual environment (le librerie sono installate lì dentro):

```bash
source .venv/bin/activate
```

Quando è attivo, vedi `(.venv)` all'inizio della riga del terminale.
Per uscire: `deactivate`.

> In alternativa, senza attivare, puoi sempre usare il percorso diretto:
> `.venv/bin/python scripts/...`

---

## 2. Avviare la dashboard

```bash
python scripts/viz/dashboard.py
```

Apri **http://127.0.0.1:8050**. Quattro tab:

| Tab | Cosa mostra |
|---|---|
| 📈 Grafico | Candlestick + Volume + RSI + MACD per ogni titolo, con EMA e Bollinger. Riquadro "Cosa sto guardando?" con le spiegazioni |
| 🟩 Heatmap settoriale | I 66 titoli colorati per performance (verde = su, rosso = giù) |
| 📊 Settori nel tempo | Crescita % di ogni settore, da 6 mesi a 5 anni |
| 💾 Database | Candele e copertura per ogni ticker |

La dashboard aggrega le candele in base al periodo (15 min → settimanali) per restare fluida anche su 5 anni.

---

## 3. Eseguire gli script

Sempre con l'ambiente attivo (`source .venv/bin/activate`):

| Cosa | Comando | Quando serve |
|---|---|---|
| Verifica connessione Polygon | `python scripts/setup/verify_connection.py` | Prima di scaricare |
| Scarica storico (una tantum, ~8h) | `python scripts/data/download_history.py` | Già fatto — non rifare |
| Scarica dati macro FRED | `python scripts/data/download_macro.py` | Se mancano/aggiornare |
| Assembla dataset di training | `python scripts/data/build_dataset.py` | Dopo modifiche ai dati |
| Controllo qualità base | `python scripts/data/verify_quality.py` | Controllo dati |
| Controllo qualità approfondito | `python scripts/data/deep_check.py` | Controllo dati |
| Pulizia dati META | `python scripts/data/fix_meta.py` | Solo dopo aver ri-scaricato META |

> ⚠️ Dopo aver ri-scaricato META, esegui sempre `fix_meta.py` e poi `build_dataset.py` (vedi spiegazione nel README principale).

---

## 4. Esplorare il database

Apri `DuckDB.session.sql` in VS Code con l'estensione **SQLTools + DuckDB driver**, posizionati su una query e premi **Cmd + Enter**.

Oppure da terminale:
```bash
python -c "import duckdb; print(duckdb.connect('data/raw/market.duckdb', read_only=True).execute('SELECT COUNT(*) FROM candles').fetchone())"
```

---

## 5. Setup da zero (su un nuovo computer)

```bash
# 1. Crea il virtual environment e installa le librerie di base
bash scripts/setup/install.sh

# 2. Attiva l'ambiente
source .venv/bin/activate

# 3. Installa le librerie aggiuntive della dashboard e dei dati
pip install dash-bootstrap-components pyarrow

# 4. Crea il file config/.env con le tue API key:
#    POLYGON_API_KEY=la_tua_key      (https://polygon.io)
#    FRED_API_KEY=la_tua_key         (https://fred.stlouisfed.org/docs/api/api_key.html)

# 5. Verifica la connessione
python scripts/setup/verify_connection.py
```

> Il database `data/raw/market.duckdb` e il dataset `data/processed/dataset.parquet` **non sono su GitHub** (troppo pesanti). Su un nuovo computer vanno rigenerati con `download_history.py` → `download_macro.py` → `build_dataset.py`, oppure copiati a mano.

---

## 6. Risoluzione problemi

**`source .venv/bin/activate` o `python` non funzionano**
Il virtual environment potrebbe essere danneggiato (capita se la cartella viene duplicata nel Finder). La soluzione più semplice è ricrearlo:
```bash
rm -rf .venv
bash scripts/setup/install.sh
source .venv/bin/activate
pip install dash-bootstrap-components pyarrow
```

**`Address already in use` / porta 8050 occupata**
La dashboard è già in esecuzione in un altro terminale. Chiudila, oppure libera la porta:
```bash
lsof -ti:8050 | xargs kill -9
```

**`ModuleNotFoundError`**
Hai dimenticato di attivare l'ambiente. Esegui `source .venv/bin/activate` e riprova.

**La dashboard si apre ma i grafici sono vuoti**
Verifica che il database esista: `ls -lh data/raw/market.duckdb`. Se manca, vanno riscaricati i dati (vedi punto 5).

---

*AI Market Predictor — Fase 1 completata. Per i dettagli del progetto vedi [README.md](README.md).*
