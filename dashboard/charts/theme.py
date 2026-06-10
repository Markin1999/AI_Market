"""
Tema grafico condiviso: colori, palette del tema scuro e layout di base.

Tutti i grafici importano da qui, così l'aspetto resta coerente in tutta la
dashboard. Per cambiare i colori dell'intera applicazione, modifichi SOLO
questo file: nessun altro file contiene codici colore "scritti a mano".
"""

# ── Colore di ogni settore ───────────────────────────────────────────────────
# Usato in: heatmap settoriale, crescita settori, intestazioni della tabella DB.
SECTOR_COLORS = {
    "Technology":             "#6366f1",
    "Financials":             "#0ea5e9",
    "Health Care":            "#10b981",
    "Consumer Discretionary": "#f59e0b",
    "Consumer Staples":       "#84cc16",
    "Energy":                 "#ef4444",
    "Industrials":            "#8b5cf6",
    "Materials":              "#f97316",
    "Real Estate":            "#ec4899",
    "Utilities":              "#14b8a6",
    "Communication Services": "#a78bfa",
}

# ── Palette del tema scuro ───────────────────────────────────────────────────
BG_PAGE   = "#0a0f1e"   # sfondo della pagina
BG_PANEL  = "#0f172a"   # sfondo dei grafici e dei pannelli
GRID      = "#1e293b"   # linee della griglia
ZEROLINE  = "#334155"   # linea dello zero
BORDER    = "#1e293b"   # bordi delle card
SPIKE     = "#475569"   # linee di puntamento (hover)
TEXT      = "#e2e8f0"   # testo principale
TEXT_MUTED= "#94a3b8"   # testo secondario
ACCENT    = "#818cf8"   # viola — colore identitario della dashboard
GREEN     = "#22c55e"   # rialzo
RED       = "#ef4444"   # ribasso
FONT      = "Inter, system-ui, sans-serif"


def base_layout(**overrides) -> dict:
    """
    Restituisce il dizionario di layout scuro comune a tutti i grafici.
    Si usa così:  fig.update_layout(**base_layout(height=600, title=...))
    Gli `overrides` sovrascrivono o aggiungono voci specifiche del grafico.
    """
    layout = dict(
        template="plotly_dark",
        paper_bgcolor=BG_PANEL,
        plot_bgcolor=BG_PANEL,
        font=dict(family=FONT, color=TEXT),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    layout.update(overrides)
    return layout
