#!/bin/bash
# Passo 1 — Setup ambiente AI Market Predictor

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

echo "=== AI Market Predictor — Setup Ambiente ==="
echo "Progetto: $PROJECT_ROOT"

# Usa Python 3.12 se disponibile (richiesto da pandas-ta >= 0.4)
PYTHON_BIN="python3"
if [ -x "/opt/homebrew/bin/python3.12" ]; then
    PYTHON_BIN="/opt/homebrew/bin/python3.12"
fi

# Crea virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "→ Creazione virtual environment con $PYTHON_BIN..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
else
    EXISTING_PY=$("$VENV_DIR/bin/python" --version 2>&1)
    if echo "$EXISTING_PY" | grep -q "Python 3.9"; then
        echo ""
        echo "→ Virtual environment esistente usa Python 3.9 — lo ricreo con Python 3.12..."
        rm -rf "$VENV_DIR"
        "$PYTHON_BIN" -m venv "$VENV_DIR"
    else
        echo ""
        echo "→ Virtual environment già esistente ($EXISTING_PY)."
    fi
fi

# Attiva e installa
source "$VENV_DIR/bin/activate"

echo "→ Aggiornamento pip..."
pip install --upgrade pip --quiet

echo "→ Installazione librerie..."
pip install \
    duckdb==0.10.3 \
    pandas-ta==0.4.71b0 \
    plotly==5.22.0 \
    polygon-api-client==1.14.2 \
    python-dotenv==1.0.1 \
    requests==2.32.4 \
    dash==2.17.1 \
    --quiet

echo ""
echo "✓ Installazione completata."
echo ""
echo "Per attivare l'ambiente in futuro:"
echo "  source .venv/bin/activate"
echo ""
echo "Prossimo passo: aggiungi la tua API key in config/.env"
echo "  POLYGON_API_KEY=la_tua_key_qui"
