"""
Catalogo degli indicatori — la fonte di verità unica della dashboard.

Ogni indicatore calcolato nel database è descritto QUI una volta sola: nome,
categoria, colonne del DB, com'è fatto, come si legge. Da questo catalogo
nascono automaticamente:
    • il glossario (tab "Indicatori")  → descrizioni
    • i selettori a tendina            → nome + colonne
    • i grafici                        → quali colonne disegnare e come

Vuoi aggiungere o cambiare la spiegazione di un indicatore? Modifichi SOLO
questo file: glossario, menu e grafici si aggiornano da soli.

Campi di ogni voce
    key        identificativo breve (valore dei menu a tendina)
    name       nome leggibile mostrato all'utente
    category   gruppo (Momentum, Volatilità, ...)
    cols       colonne del DB che compongono l'indicatore
    short      "cos'è" — una frase
    how        "come si legge" — l'interpretazione operativa
    unit       scala dei valori ("0–100", "±", "prezzo", ...) → guida le linee guida
    overlay    True = si disegna SOPRA il prezzo; False = pannello a sé
    pattern    True = pattern candela (segnato con frecce, valori 100/0/-100)
    comparable True = ha senso confrontarlo tra titoli diversi (grafico per settore)
    sector_col colonna usata nel grafico per settore (default: la prima di cols)
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Indicator:
    key: str
    name: str
    category: str
    cols: tuple
    short: str
    how: str
    unit: str = ""
    overlay: bool = False
    pattern: bool = False
    comparable: bool = False
    sector_col: str = ""

    @property
    def primary(self) -> str:
        """Colonna principale usata nei confronti per settore."""
        return self.sector_col or self.cols[0]


# Ordine e colore di ogni categoria (usati per raggruppare il glossario)
CATEGORY_ORDER = [
    "Momentum",
    "Trend — direzione",
    "Trend — forza",
    "Volatilità",
    "Volume",
    "Ichimoku",
    "Pattern candele",
]
CATEGORY_COLORS = {
    "Momentum":          "#a78bfa",
    "Trend — direzione": "#38bdf8",
    "Trend — forza":     "#f59e0b",
    "Volatilità":        "#94a3b8",
    "Volume":            "#22c55e",
    "Ichimoku":          "#ec4899",
    "Pattern candele":   "#f97316",
}


_ALL = [
    # ── Momentum ──────────────────────────────────────────────────────────────
    Indicator("rsi", "RSI (14)", "Momentum", ("rsi",),
        "Forza relativa del movimento: confronta la dimensione dei rialzi con quella dei ribassi recenti.",
        "Sopra 70 = ipercomprato (possibile calo). Sotto 30 = ipervenduto (possibile rimbalzo). Intorno a 50 = equilibrio.",
        unit="0–100", comparable=True),
    Indicator("stoch", "Stocastico (14,3,3)", "Momentum", ("stoch_k", "stoch_d"),
        "Dove si trova la chiusura rispetto al range massimo-minimo degli ultimi periodi.",
        "Sopra 80 = ipercomprato, sotto 20 = ipervenduto. L'incrocio della linea veloce (K) sopra la lenta (D) è un segnale rialzista.",
        unit="0–100", comparable=True, sector_col="stoch_k"),
    Indicator("roc", "ROC (10)", "Momentum", ("roc",),
        "Rate of Change: variazione percentuale del prezzo rispetto a 10 candele fa.",
        "Positivo = il prezzo accelera al rialzo, negativo = al ribasso. Più è lontano da 0, più il movimento è forte.",
        unit="±%", comparable=True),
    Indicator("williams_r", "Williams %R (14)", "Momentum", ("williams_r",),
        "Come lo stocastico ma su scala invertita: misura quanto la chiusura è lontana dal massimo recente.",
        "Vicino a 0 = ipercomprato, vicino a -100 = ipervenduto. Le soglie tipiche sono -20 e -80.",
        unit="-100–0", comparable=True),
    Indicator("cci", "CCI (14)", "Momentum", ("cci",),
        "Commodity Channel Index: quanto il prezzo si discosta dalla sua media tipica.",
        "Sopra +100 = trend rialzista forte, sotto -100 = trend ribassista forte. Tra -100 e +100 = fase laterale.",
        unit="±", comparable=True),

    # ── Trend — direzione ─────────────────────────────────────────────────────
    Indicator("macd", "MACD (12,26,9)", "Trend — direzione", ("macd", "macd_signal", "macd_hist"),
        "Differenza tra una media veloce e una lenta del prezzo, con la sua linea di segnale e l'istogramma.",
        "Linea MACD sopra la Signal = momentum rialzista. Istogramma che cresce = il movimento accelera; che si accorcia = sta rallentando.",
        unit="±"),
    Indicator("ema", "EMA 20 / 50 / 200", "Trend — direzione", ("ema_20", "ema_50", "ema_200"),
        "Medie mobili esponenziali dei prezzi su breve (20), medio (50) e lungo periodo (200).",
        "Prezzo sopra le medie = tendenza rialzista. La EMA 200 è il trend di fondo; l'incrocio della 50 sopra la 200 è un classico segnale rialzista.",
        unit="prezzo", overlay=True),
    Indicator("psar", "Parabolic SAR", "Trend — direzione", ("psar_long", "psar_short"),
        "Punti che seguono il prezzo e si ribaltano quando la tendenza cambia (colonna psar_reversal = 1 nel ribaltamento).",
        "Punti sotto il prezzo = trend rialzista (stop sotto). Punti sopra = trend ribassista. Quando saltano dall'altra parte, la tendenza è cambiata.",
        unit="prezzo", overlay=True),
    Indicator("aroon", "Aroon (25)", "Trend — direzione", ("aroon_up", "aroon_down", "aroon_osc"),
        "Da quanto tempo non si toccava un nuovo massimo (up) o minimo (down) negli ultimi 25 periodi.",
        "Aroon Up vicino a 100 = trend rialzista solido. L'oscillatore (up − down) positivo = rialzo, negativo = ribasso.",
        unit="0–100", comparable=True, sector_col="aroon_osc"),

    # ── Trend — forza ─────────────────────────────────────────────────────────
    Indicator("adx", "ADX (14)", "Trend — forza", ("adx", "adx_plus", "adx_minus"),
        "Misura quanto è FORTE un trend (non la direzione), con le componenti rialzista (+DI) e ribassista (−DI).",
        "ADX sopra 25 = trend forte, sotto 20 = mercato laterale. +DI sopra −DI = forza ai compratori; viceversa ai venditori.",
        unit="0–100", comparable=True),

    # ── Volatilità ────────────────────────────────────────────────────────────
    Indicator("bbands", "Bollinger Bands (20,2)", "Volatilità", ("bb_upper", "bb_mid", "bb_lower"),
        "Una media mobile con due bande a distanza di 2 deviazioni standard: si allargano quando la volatilità sale.",
        "Prezzo sulla banda alta = forse troppo caro; sulla bassa = forse a sconto. Bande strette = calma prima di un movimento forte.",
        unit="prezzo", overlay=True),
    Indicator("atr", "ATR (14)", "Volatilità", ("atr",),
        "Average True Range: ampiezza media del movimento di prezzo, in punti (volatilità assoluta).",
        "ATR alto = candele ampie, mercato nervoso. Si usa per dimensionare stop-loss proporzionati alla volatilità.",
        unit="prezzo (punti)"),
    Indicator("donchian", "Donchian (20)", "Volatilità", ("dc_upper", "dc_lower"),
        "Il massimo e il minimo degli ultimi 20 periodi: il \"canale\" entro cui il prezzo si è mosso.",
        "Rottura sopra il canale = possibile inizio di trend rialzista; rottura sotto = ribassista. Base delle strategie breakout.",
        unit="prezzo", overlay=True),
    Indicator("keltner", "Keltner (20,2)", "Volatilità", ("kc_upper", "kc_lower"),
        "Canale intorno alla media basato sull'ATR (volatilità reale) invece che sulla deviazione standard.",
        "Prezzo che esce dal canale = movimento forte. Confrontato con Bollinger aiuta a distinguere trend da volatilità.",
        unit="prezzo", overlay=True),

    # ── Volume ────────────────────────────────────────────────────────────────
    Indicator("obv", "OBV", "Volume", ("obv",),
        "On-Balance Volume: somma cumulata dei volumi, che sale nelle candele verdi e scende in quelle rosse.",
        "Se sale insieme al prezzo conferma il trend. Se prezzo sale ma OBV no (divergenza), il movimento è debole.",
        unit="cumulato"),
    Indicator("mfi", "MFI (14)", "Volume", ("mfi",),
        "Money Flow Index: come l'RSI ma pesato per i volumi — il \"denaro\" che entra ed esce.",
        "Sopra 80 = ipercomprato, sotto 20 = ipervenduto. Più affidabile dell'RSI perché tiene conto di quanto si è scambiato.",
        unit="0–100", comparable=True),
    Indicator("cmf", "CMF (20)", "Volume", ("cmf",),
        "Chaikin Money Flow: flusso netto di denaro (accumulo vs distribuzione) negli ultimi 20 periodi.",
        "Sopra 0 = i compratori dominano (accumulo), sotto 0 = i venditori (distribuzione). Più lontano da 0, più la pressione è forte.",
        unit="-1–+1", comparable=True),
    Indicator("force_index", "Force Index (13)", "Volume", ("force_index",),
        "Combina direzione del prezzo e volume per misurare la \"forza\" dietro ogni movimento.",
        "Positivo e crescente = spinta rialzista convinta. Negativo = pressione in vendita. Gli zeri segnalano cambi di equilibrio.",
        unit="±"),

    # ── Ichimoku ──────────────────────────────────────────────────────────────
    Indicator("ichimoku", "Ichimoku", "Ichimoku",
        ("ichi_tenkan", "ichi_kijun", "ichi_span_a", "ichi_span_b", "ichi_chikou"),
        "Sistema giapponese completo: due linee di tendenza (Tenkan, Kijun), una \"nuvola\" (Span A/B) e una linea ritardata (Chikou).",
        "Prezzo sopra la nuvola = trend rialzista, sotto = ribassista, dentro = incertezza. La nuvola è anche supporto/resistenza.",
        unit="prezzo", overlay=True),

    # ── Pattern candele (frecce sul prezzo, valori 100 / 0 / -100) ────────────
    Indicator("cdl_doji", "Doji", "Pattern candele", ("cdl_doji",),
        "Candela con apertura e chiusura quasi uguali: il mercato è indeciso.",
        "Spesso anticipa un'inversione, soprattutto dopo un trend deciso. Va confermato dalla candela successiva.",
        pattern=True),
    Indicator("cdl_hammer", "Hammer (martello)", "Pattern candele", ("cdl_hammer",),
        "Corpo piccolo in alto con una lunga ombra inferiore, dopo una discesa.",
        "Segnale di inversione rialzista: i venditori hanno spinto giù ma i compratori hanno ripreso il controllo.",
        pattern=True),
    Indicator("cdl_inverted_hammer", "Inverted Hammer", "Pattern candele", ("cdl_inverted_hammer",),
        "Martello rovesciato: corpo piccolo in basso, lunga ombra superiore, dopo una discesa.",
        "Possibile inversione rialzista in arrivo, da confermare con una candela verde successiva.",
        pattern=True),
    Indicator("cdl_engulfing", "Engulfing", "Pattern candele", ("cdl_engulfing",),
        "Una candela il cui corpo \"ingloba\" completamente quello della precedente.",
        "Verde che ingloba una rossa = inversione rialzista; rossa che ingloba una verde = ribassista. Segnale forte.",
        pattern=True),
    Indicator("cdl_harami", "Harami", "Pattern candele", ("cdl_harami",),
        "Una candela piccola tutta contenuta nel corpo di quella precedente, più grande.",
        "Segnala che il movimento sta perdendo forza: possibile pausa o inversione del trend in corso.",
        pattern=True),
    Indicator("cdl_morning_star", "Morning Star", "Pattern candele", ("cdl_morning_star",),
        "Schema a tre candele (rossa → piccola → verde) che appare dopo una discesa.",
        "Una delle inversioni rialziste più affidabili: la 'stella del mattino' che annuncia la ripresa.",
        pattern=True),
    Indicator("cdl_evening_star", "Evening Star", "Pattern candele", ("cdl_evening_star",),
        "Schema a tre candele (verde → piccola → rossa) che appare dopo una salita.",
        "L'opposto della Morning Star: inversione ribassista, la 'stella della sera' che annuncia il calo.",
        pattern=True),
    Indicator("cdl_shooting_star", "Shooting Star", "Pattern candele", ("cdl_shooting_star",),
        "Corpo piccolo in basso con lunga ombra superiore, dopo una salita.",
        "Segnale di inversione ribassista: i compratori hanno spinto su ma sono stati respinti.",
        pattern=True),
    Indicator("cdl_hanging_man", "Hanging Man", "Pattern candele", ("cdl_hanging_man",),
        "Come l'Hammer (lunga ombra inferiore) ma in cima a una salita.",
        "Possibile inversione ribassista: la spinta rialzista comincia a incontrare vendite.",
        pattern=True),
]

# ── Indici e helper derivati ─────────────────────────────────────────────────
CATALOG = {ind.key: ind for ind in _ALL}

# Colonne grezze del DB presenti nel catalogo (ordine stabile), per le query
ALL_INDICATOR_COLUMNS = [c for ind in _ALL for c in ind.cols]
ALL_COLUMNS = set(ALL_INDICATOR_COLUMNS) | {"vwap"}
PATTERN_COLUMNS = {ind.cols[0] for ind in _ALL if ind.pattern}


def by_category() -> dict:
    """Restituisce {categoria: [Indicator, ...]} nell'ordine di CATEGORY_ORDER."""
    out = {cat: [] for cat in CATEGORY_ORDER}
    for ind in _ALL:
        out[ind.category].append(ind)
    return out


def chartable_options() -> list:
    """Opzioni per il multiselettore della pagina azione (tutti gli indicatori)."""
    return [{"label": f"{ind.name}  ·  {ind.category}", "value": ind.key} for ind in _ALL]


def comparable_options() -> list:
    """Opzioni per il grafico per settore (solo indicatori confrontabili tra titoli)."""
    return [{"label": f"{ind.name}  ·  {ind.category}", "value": ind.key}
            for ind in _ALL if ind.comparable]
