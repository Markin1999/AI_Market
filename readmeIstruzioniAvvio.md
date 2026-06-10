# 🚀 Istruzioni di avvio — AI Market Predictor

Guida **operativa**: solo i comandi per avviare e usare il progetto.
Per sapere *cosa contiene ogni cartella* → [readme_Istruzioni_cartelle.md](readme_Istruzioni_cartelle.md).

> ⚠️ **Lancia sempre i comandi dalla cartella principale**, altrimenti gli script non trovano `shared/` e `data/`:
> ```bash
> cd /Users/marcofilannino/Desktop/ai_market_predictor
> ```

---

## ⚡ Avvio rapido — la dashboard

```bash
source .venv/bin/activate
python dashboard/app.py
```
→ apri **http://127.0.0.1:8050** · ferma con **Ctrl + C**.

Tab disponibili: 📈 Grafico (candele + RSI/MACD/EMA/Bollinger) · 🟩 Heatmap settoriale · 📊 Settori nel tempo · 💾 Database.
Architettura della dashboard → [dashboard/README.md](dashboard/README.md).

---

## 🐍 Ambiente Python

```bash
source .venv/bin/activate     # attiva — vedi "(.venv)" nel prompt
deactivate                    # esci
```
Senza attivare puoi usare il percorso diretto: `.venv/bin/python data_pipeline/...`

---

## 🧰 Comandi della pipeline dati

Con l'ambiente attivo:

| Comando | Cosa fa | Quando |
|---|---|---|
| `python data_pipeline/verify_connection.py` | Verifica la API key Polygon | Prima di scaricare |
| `python data_pipeline/download_history.py` | Scarica lo storico 15 min (~8h) | Già fatto — non rifare |
| `python data_pipeline/download_macro.py` | Scarica i dati macro FRED | Per aggiornare |
| `python data_pipeline/recalculate_indicators.py` | Ricalcola tutti gli indicatori sul DB | Dopo modifiche a `calculate.py` |
| `python data_pipeline/build_dataset.py` | Assembla `dataset.parquet` | Dopo modifiche ai dati |
| `python data_pipeline/verify_quality.py` | Controllo qualità base | Controllo dati |
| `python data_pipeline/deep_check.py` | Controllo qualità approfondito | Controllo dati |
| `python data_pipeline/fix_meta.py` | Pulizia dati META | Solo dopo aver ri-scaricato META |
| `python data_pipeline/restore_from_parquet.py AAPL NVDA` | Ripristina ticker dal parquet | Recupero d'emergenza |

> ⚠️ **Polygon serve solo ~2 anni di storico.** Non ri-scaricare ticker che hanno già i 5 anni completi nel DB — perderesti 3 anni. Lo storico esistente è insostituibile.
>
> ⚠️ Dopo aver ri-scaricato META: prima `fix_meta.py`, poi `build_dataset.py`.

---

## 🔍 Esplorare il database

**VS Code:** apri `DuckDB.session.sql` (estensione *SQLTools + DuckDB driver*), poi `Cmd + Enter` su una query.

**Terminale:**
```bash
python -c "import duckdb; print(duckdb.connect('data/raw/market.duckdb', read_only=True).execute('SELECT COUNT(*) FROM candles').fetchone())"
```

---

## 🆕 Setup da zero (nuovo computer)

```bash
brew install ta-lib                                   # serve per i pattern candele
bash data_pipeline/install.sh                         # crea .venv + librerie base
source .venv/bin/activate
pip install dash-bootstrap-components pyarrow TA-Lib   # librerie extra
```
Poi crea il file `shared/config/.env` con le tue API key:
```
POLYGON_API_KEY=la_tua_key      # https://polygon.io
FRED_API_KEY=la_tua_key         # https://fred.stlouisfed.org/docs/api/api_key.html
```
E verifica: `python data_pipeline/verify_connection.py`

> `data/raw/market.duckdb` e `data/processed/dataset.parquet` **non sono su GitHub** (pesanti). Vanno copiati a mano, oppure rigenerati: `download_history.py` → `download_macro.py` → `build_dataset.py`.

---

## 🛠️ Risoluzione problemi

**`ModuleNotFoundError: 'shared'` o `'data_pipeline'`** → stai lanciando dalla cartella sbagliata. Torna nella root del progetto e rilancia.

**`ModuleNotFoundError` su una libreria (dash, pyarrow…)** → ambiente non attivo: `source .venv/bin/activate`.

**`source .venv/bin/activate` non funziona** → venv danneggiato. Ricrealo:
```bash
rm -rf .venv && bash data_pipeline/install.sh
source .venv/bin/activate && pip install dash-bootstrap-components pyarrow TA-Lib
```

**`Address already in use` / porta 8050 occupata** → la dashboard è già aperta. Liberala:
```bash
lsof -ti:8050 | xargs kill -9
```

**`IO Error: Could not set lock ... market.duckdb`** → un altro processo (di solito la dashboard) tiene aperto il DB. Chiudilo prima di lanciare script che scrivono.

**Dashboard aperta ma grafici vuoti** → database mancante. Controlla con `ls -lh data/raw/market.duckdb`; se manca, rigenera i dati.

---

*Fase 1 completata · Fase 2 in corso. Dettagli progetto → [README.md](README.md) · Mappa cartelle → [readme_Istruzioni_cartelle.md](readme_Istruzioni_cartelle.md).*
