# training/ — Fase 2: l'addestramento del bambino

Questa cartella contiene il codice dell'**addestramento** (Reinforcement Learning), separato dalla pipeline dati.

## Cosa fa

Qui vive il "cervello" che impara: a partire dallo Stadio 1 (Vedere) con il VQ-VAE, fino agli stadi successivi.

## Cosa usa (e cosa NON usa)

- **Legge** il database `data/raw/market.duckdb` — le candele con i ~45 indicatori già calcolati dalla pipeline dati.
- **Usa** `shared/` per la configurazione (lista titoli, settori) e per il calcolo indicatori — *una sola copia*, condivisa con la pipeline, così non divergono mai.
- **NON** scarica da Polygon, **non** usa API key, **non** tocca la pipeline dati.

## Output

- Modelli addestrati → cartella `models/` (nella root, condivisa).
- Memoria dei pattern → `models/pattern_memory/`.

## Stato

In fase di progettazione. L'architettura (VQ-VAE + memoria pattern, finestra candele, normalizzazione) è discussa nella roadmap della Fase 2 in [Regole/Roadmap delle fasi/](../Regole/Roadmap%20delle%20fasi/).
