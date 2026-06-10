# 📊 Dashboard — Software di visualizzazione

Applicazione **locale** per esplorare il database: grafici a candele, indicatori, heatmap settoriali, crescita dei settori. Gira sul tuo computer, non è un sito web pubblicato.

> **È un software, non una pagina web.** Non è un unico file gigante: è diviso in **componenti**, ognuno nella sua cartella, ognuno con un compito solo. Così puoi capire e modificare un pezzo senza toccare il resto.

---

## Come si avvia

```bash
source .venv/bin/activate
python dashboard/app.py
```
Apri **http://127.0.0.1:8050** nel browser · fermi con **Ctrl + C**.

> ⚠️ Lancialo dalla cartella principale del progetto, non da dentro `dashboard/`.

---

## L'idea: ogni cosa al suo posto

Immagina la dashboard come una cucina. Non c'è un unico cuoco che fa tutto: ci sono reparti separati. Ogni reparto è una cartella.

```
dashboard/
│
├── app.py            ← IL MAITRE: mette insieme i pezzi e apre il locale
│
├── indicators/       ← IL RICETTARIO: descrizione di ogni indicatore (fonte unica)
├── data/             ← LA DISPENSA: prende i dati dal database
├── charts/           ← LA CUCINA: trasforma i dati in grafici
├── components/       ← I MATTONCINI: pezzi di interfaccia riutilizzabili
├── tabs/             ← LE SALE: le 7 schermate che vedi in alto
└── callbacks/        ← I CAMERIERI: quando tocchi un controllo, portano il grafico aggiornato
```

**Il flusso di un'azione**, es. "cambio ticker da AAPL a MSFT":

```
tu cambi il dropdown
      │
      ▼
callbacks/  ──chiama──▶  charts/  ──chiede i dati──▶  data/  ──interroga──▶  market.duckdb
      │                     │                                                      │
      │                     ◀──────────────── DataFrame con le candele ───────────┘
      ▼
il grafico aggiornato torna a schermo
```

---

## Le cartelle, una per una

### 📁 `indicators/` — il ricettario (catalogo degli indicatori)

Il **cuore informativo** della dashboard. Un solo file descrive *tutti* gli indicatori: nome, categoria, colonne del database, cos'è e come si legge. Da qui nascono **automaticamente** il glossario, i menu a tendina e i grafici.

| File | Cosa fa | Quando lo tocchi |
|---|---|---|
| `catalog.py` | La **fonte di verità unica**: una voce per ogni indicatore con descrizione, colonne e regole di disegno | Per aggiungere un indicatore, cambiare una spiegazione o un nome |

> 🧠 **La regola d'oro:** vuoi che un indicatore compaia (con la sua spiegazione) nel glossario, nei menu e nei grafici? Aggiungi una voce in `catalog.py`. Non devi toccare nient'altro.

### 📁 `data/` — la dispensa (accesso al database)

Qui vivono **solo le query**. Nessun grafico, nessuna grafica: solo "prendi questi dati dal database". Se vuoi cambiare *cosa* viene letto, modifichi qui.

| File | Cosa fa | Quando lo tocchi |
|---|---|---|
| `connection.py` | Apre **una** connessione al DB (sola lettura) e la riusa | Quasi mai — solo se cambia il percorso del DB |
| `candles.py` | Carica le candele, le aggrega per timeframe e le mette in **cache** | Se vuoi cambiare gli intervalli (15min/1h/...) o la cache |
| `indicators.py` | Legge gli indicatori **memorizzati** nel DB: tutti quelli di un titolo, o uno per tutto un settore | Se cambi come si campionano gli indicatori salvati |
| `heatmap.py` | Calcola la performance % di ogni titolo | Se cambi come si misura la performance |
| `sectors.py` | Estrae la chiusura giornaliera di ogni titolo | Se cambi cosa mostra il grafico settori |
| `stats.py` | Conta candele e periodo per ogni ticker | Se vuoi altre statistiche nella tab Database |

> ℹ️ **Due modi di leggere gli indicatori.** `candles.py` li *ricalcola* sul timeframe mostrato (per il grafico interattivo "📈 Grafico"). `indicators.py` legge invece quelli *già salvati* nel database (per la pagina "🔬 Azione" e i confronti per settore): così vedi esattamente i dati che abbiamo calcolato.

### 📁 `charts/` — la cucina (costruzione dei grafici)

Qui i dati diventano grafici Plotly. **Un file per ogni tipo di grafico.** Se vuoi cambiare l'aspetto di un grafico, sai esattamente dove andare.

| File | Grafico | Quando lo tocchi |
|---|---|---|
| `theme.py` | **Colori e stile** condivisi da tutti i grafici | Per cambiare i colori di TUTTA la dashboard |
| `candlestick.py` | Grafico a candele + volume + RSI + MACD | Per modificare il grafico principale |
| `stock_detail.py` | Pagina azione: prezzo + indicatori componibili (overlay, pannelli, pattern) | Per modificare come si disegnano gli indicatori del titolo |
| `sector_indicator.py` | Un indicatore confrontato tra i titoli di un settore | Per modificare il confronto per settore |
| `heatmap.py` | Heatmap settoriale | Per modificare la heatmap |
| `sector_growth.py` | Linee di crescita dei settori | Per modificare il grafico settori |

> 🎨 **Vuoi cambiare un colore ovunque?** Tocchi solo `charts/theme.py`. Nessun altro file contiene codici colore scritti a mano.

### 📁 `components/` — i mattoncini (pezzi di interfaccia)

Pezzi di grafica **riutilizzabili**, usati in più punti. Costruiti una volta, usati ovunque.

| File | Cosa fa |
|---|---|
| `header.py` | L'intestazione in alto con titolo e contatori |
| `info_card.py` | La cardina con icona + spiegazione (quelle del pannello "Cosa sto guardando?") |
| `options.py` | Le liste condivise dei menu (ticker, periodi), così non divergono tra le tab |

### 📁 `tabs/` — le sale (le 7 schermate)

Ogni tab che vedi in alto è un file. Una tab mette insieme i controlli (dropdown) + i mattoncini + lo spazio dove comparirà il grafico.

| File | Tab | Cosa contiene |
|---|---|---|
| `chart_tab.py` | 📈 Grafico | Dropdown ticker/periodo, checkbox overlay, pannello spiegazioni, grafico candele |
| `stock_tab.py` | 🔬 Azione | Dropdown ticker/periodo + multiselettore indicatori, grafico componibile del titolo |
| `sector_indicator_tab.py` | 🧭 Indicatori per settore | Dropdown indicatore/settore/periodo + grafico di confronto |
| `heatmap_tab.py` | 🟩 Heatmap settoriale | Dropdown periodo + heatmap |
| `growth_tab.py` | 📊 Settori nel tempo | Dropdown periodo + grafico linee |
| `glossary_tab.py` | 📚 Indicatori | Glossario: una card per indicatore, generata dal catalogo (senza grafici) |
| `database_tab.py` | 💾 Database | Card riassuntive + tabella dei ticker |

### 📁 `callbacks/` — i camerieri (la logica interattiva)

Un "callback" collega un controllo a un grafico: *"quando l'utente cambia X, ricalcola e mostra Y"*. Tutta la logica interattiva è in un posto solo.

| File | Cosa fa |
|---|---|
| `register.py` | Registra i 5 callback: ogni controllo (ticker, periodo, overlay, indicatori, settore) → ridisegna il grafico giusto |

### 📄 `app.py` — il maître (entry point)

L'unico file da lanciare. Fa solo 4 cose: crea l'app, carica le statistiche una volta, monta il layout (intestazione + 4 tab), registra i callback. Non contiene logica di grafici o query: solo "assemblaggio".

---

## Tutti i grafici, spiegati

### 📈 Grafico a candele (tab "Grafico")

Quattro riquadri impilati che condividono lo stesso asse del tempo:

1. **Candele giapponesi** — ogni candela è un intervallo di tempo. Corpo verde = chiusura sopra apertura (salita), rosso = discesa. Gli "stoppini" sono massimo e minimo toccati.
   - **EMA 20/50/200** (linee gialla/arancio/viola): medie mobili. Prezzo sopra = tendenza su. La 200 è il trend di fondo.
   - **Bollinger Bands** (banda grigia): volatilità. Prezzo vicino al bordo alto = caro, al bordo basso = a sconto.
2. **Volume** — barre verdi/rosse: quante azioni scambiate. Volume alto = movimento affidabile.
3. **RSI (0–100)** — forza del movimento. Sopra 70 (zona rossa) ipercomprato, sotto 30 (zona verde) ipervenduto.
4. **MACD** — cambi di tendenza. Linea blu che incrocia l'arancione verso l'alto = momentum su; le barre = forza del segnale.

**Timeframe adattivo:** il periodo scelto decide l'aggregazione delle candele, così a schermo arrivano sempre poche centinaia di punti (veloce) invece di milioni.

| Periodo | Candele mostrate |
|---|---|
| 1 settimana | 15 minuti |
| 1 mese | 1 ora |
| 3 mesi | 4 ore |
| 6 mesi – 2 anni | giornaliere |
| 5 anni | settimanali |

### 🔬 Pagina azione (tab "Azione")

La scheda completa di un singolo titolo, con **tutti gli indicatori che abbiamo calcolato** nel database. Scegli ticker e periodo, poi aggiungi/togli indicatori dal menu: il grafico si ricompone da solo.

- Il **prezzo a candele** è sempre il pannello in alto.
- Gli indicatori **overlay** (EMA, Bollinger, PSAR, Donchian, Keltner, Ichimoku) si disegnano *sopra* il prezzo.
- I **pattern candele** appaiono come frecce: ▲ verde (rialzista) sotto la candela, ▼ rossa (ribassista) sopra.
- Ogni **oscillatore** (RSI, MACD, ADX, Stocastico, ...) prende un **pannello tutto suo** sotto il prezzo, con le sue linee guida (es. 70/30 per l'RSI).

> A differenza della tab "Grafico" (che ricalcola gli indicatori sul timeframe), qui leggi i **valori salvati nel database**, campionati alla chiusura di ogni intervallo. È la vista fedele ai dati che abbiamo.

### 🧭 Indicatori per settore (tab "Indicatori per settore")

Lo **stesso indicatore** disegnato per **tutti i titoli di un settore**, sovrapposti. Scegli indicatore + settore + periodo. Serve a confrontare a colpo d'occhio: chi è ipercomprato, chi ipervenduto, chi guida il movimento. Il menu offre solo gli indicatori **confrontabili** tra titoli (oscillatori normalizzati come RSI, Stocastico, MFI, ADX...): gli indicatori in scala-prezzo non sono comparabili tra titoli con prezzi diversi, quindi non compaiono qui.

### 📚 Glossario indicatori (tab "Indicatori")

Non è un grafico: è la **pagina informativa di ogni indicatore**. Una card per indicatore, raggruppate per categoria, con: nome, scala dei valori, *cos'è* e *come si legge*. In fondo a ogni card, in grigio, i nomi delle colonne nel database. È generata **automaticamente dal catalogo**: aggiungi un indicatore in `indicators/catalog.py` e qui compare da solo.

### 🟩 Heatmap settoriale (tab "Heatmap")

Tutti i 66 titoli in una griglia, una riga per settore. Ogni cella colorata in base alla performance % del periodo: verde = su, rosso = giù. Serve a vedere a colpo d'occhio quali settori si muovono insieme.

### 📊 Crescita settori (tab "Settori nel tempo")

Una linea per settore, tutte partono da 0% all'inizio del periodo. Confronta chi è cresciuto di più a prescindere dal prezzo assoluto. L'indice di settore è la media equipesata dei suoi titoli. Click sulla legenda per isolare un settore.

### 💾 Stato database (tab "Database")

Non è un grafico ma una tabella: quante candele per ogni titolo e il periodo coperto. Serve a verificare che i dati siano completi prima di addestrare il modello.

---

## Come modificarlo — ricette pratiche

**Cambiare un colore in tutta la dashboard**
→ `charts/theme.py`, modifica `SECTOR_COLORS` o le costanti (`GREEN`, `BG_PANEL`, ...).

**Aggiungere un indicatore alla pagina azione, al glossario e ai menu** (la ricetta principale)
→ Una sola mossa: aggiungi una voce in `indicators/catalog.py`. Specifichi nome, categoria, colonne del DB, descrizione (`short` + `how`), scala (`unit`) e se è un overlay sul prezzo. Comparirà automaticamente nel glossario, nel menu della pagina azione e — se lo marchi `comparable=True` — anche nel confronto per settore. (La colonna deve già esistere nel DB: si crea nella pipeline dati.)

**Aggiungere un indicatore agli overlay del grafico a candele** (tab "Grafico")
1. `data/candles.py` → aggiungi il nome alla lista `_CHART_INDICATORS`
2. `charts/candlestick.py` → aggiungi la traccia per disegnarlo

**Aggiungere un nuovo periodo ai menu**
→ `components/options.py`, aggiungi una voce a `PERIOD_OPTIONS` (vale per tutte le tab che lo usano).

**Aggiungere un grafico completamente nuovo**
1. `data/` → un file con la query che serve
2. `charts/` → un file con la funzione `make_...()` che disegna
3. `tabs/` → un file con la nuova tab (controlli + `dcc.Graph`)
4. `callbacks/register.py` → collega il controllo al nuovo grafico
5. `app.py` → aggiungi la tab alla lista delle `dbc.Tabs`

**Cambiare la porta** (se la 8050 è occupata)
→ `app.py`, ultima riga: `app.run(debug=False, port=8060)`.

**Aprirla da telefono/altro PC sulla stessa rete**
→ `app.py`, ultima riga: aggiungi `host="0.0.0.0"`, poi apri `http://IP-DEL-MAC:8050`.

---

## Che tipo di file trovi qui

| Estensione | Cos'è |
|---|---|
| `.py` | Codice Python — tutta la logica |
| `__init__.py` | File (quasi) vuoto che rende una cartella un "pacchetto" importabile. Non si tocca |
| `README.md` | Questo file |
| `__pycache__/` | Cache automatica di Python. Si rigenera da sola, ignorala |

---

## Perché è veloce

1. **Una sola connessione** al DB, riusata (`data/connection.py`), aperta in sola lettura.
2. **Aggregazione lato database**: candele e indicatori vengono ridotti a poche centinaia di punti con `time_bucket` prima di arrivare al grafico.
3. **Cache in memoria** (`data/candles.py` e `data/indicators.py`): per la stessa coppia (ticker, periodo) i dati si caricano UNA volta. Cambiare overlay, aggiungere o togliere un indicatore dalla pagina azione è istantaneo.

---

## Dipendenze

`dash`, `dash-bootstrap-components`, `plotly`, `duckdb`, `pandas`, `pandas-ta` (per ricalcolare gli indicatori sul timeframe mostrato). Tutte già nel `.venv` del progetto. Legge da `shared/config/settings.py` (percorso DB) e `shared/indicators/calculate.py` (indicatori).

---

*Parte del progetto AI Market Predictor — vedi [README principale](../README.md), [comandi](../readmeIstruzioniAvvio.md), [mappa cartelle](../readme_Istruzioni_cartelle.md).*
