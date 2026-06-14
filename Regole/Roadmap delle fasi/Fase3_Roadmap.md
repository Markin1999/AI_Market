# AI MARKET PREDICTOR

### Fase 3 — Il Predittore (Stadio 2: Associare)

_La seconda IA: imparare a **prevedere**, non solo a vedere._

> **Stato: DA INIZIARE.** La Fase 2 ha costruito e **validato** l'occhio (Stadio 1 — Vedere). La Fase 3 costruisce la **seconda IA** — il **predittore** — che mette in pratica lo **Stadio 2 (Associare)** del piano. Vive in [`training/predittore/`](../../training/predittore/), separata dall'occhio in [`training/occhio/`](../../training/occhio/).

---

## Da dove partiamo (onestà piena)

Tre fatti, fermi:

- ✅ **L'occhio funziona.** I 3 test sono passati (giugno 2026): ricostruisce dati mai visti (rapporto test/train 1.02×), le forme sono condivise tra ~51 titoli su 66, e tornano in tutti i 6 anni. Vede strutture **reali, generali, stabili**.
- ✅ **Conosciamo il pavimento.** La sonda ([`sonda_predittiva.py`](../../training/predittore/sonda_predittiva.py)) ha misurato che la **forma grezza da sola** (1 numero su 164) **non** prevede la direzione: ~50%, come il lancio di una moneta. Nessun vantaggio sul baseline.
- ⬜ **Il predittore vero non esiste ancora.** Firma ricca + indicatori + testa che impara: tutto da costruire.

> Il risultato della sonda **non** è un fallimento: è **coerente con la finanza seria** (il prezzo passato, da solo, quasi non predice il futuro) ed era **previsto dal piano** — è proprio per questo che lo Stadio 2 aggiunge indicatori, una testa che impara e la ricompensa. La sonda ci ha dato gratis il **numero da battere**.

---

## L'obiettivo della Fase 3

Sopra l'occhio **congelato** si aggiunge una **testa decisionale**: una rete che, vista la situazione, risponde *"il prezzo salirà o scenderà nelle prossime candele?"*

- **Ingressi:** la **firma** dell'occhio (32 numeri) **+ i 45 indicatori** (per qualificare la situazione).
- **Apprendimento:** prima **supervisionato** (impara dalle risposte giuste del passato), poi con **ricompensa** (giusto → segnale positivo, sbagliato → negativo).
- **Soglia minima di successo:** accuracy direzionale **> 53% out-of-sample** — tre punti sopra il lancio di moneta, su dati mai visti.

---

## La lezione che guida la Fase 3

La sonda ha bocciato la **scorciatoia** (forma grezza → media → direzione). Le cause probabili, e cosa cambia:

| Perché la forma grezza non basta | La risposta della Fase 3 |
|---|---|
| 164 forme = archetipi troppo **generali** | usare la **firma ricca** (32 numeri), non l'etichetta |
| la forma non ha **contesto** | aggiungere i **45 indicatori** (e in futuro macro e settori) |
| una **media** non è intelligenza | una **testa che impara** |
| la direzione è il bersaglio **più difficile** | soglia onesta (53%), e si valuta sempre sul futuro |

---

## I passi concreti

| # | Passo | Risultato atteso / cancello di decisione |
|---|---|---|
| 1 | **Baseline** (fatto) — la sonda sulla forma grezza | Pavimento ≈ 50%. Numero da battere ✅ |
| 2 | **Test del segnale ricco** — firma (32) + indicatori → un classificatore equo, passato→futuro | C'è segnale? Batte 50%/53%? **Cancello:** se no, ci si ferma e si ripensa, prima di investire |
| 3 | **Testa che impara con ricompensa** — solo se il passo 2 mostra segnale | La testa supera stabilmente il baseline |
| 4 | **Definire la ricompensa** — quanto movimento, in quante candele, con quale soglia — **sui dati reali davanti** | Ricompensa documentata, non scelta a priori |
| 5 | **Valutazione rigorosa** — > 53% out-of-sample, su più orizzonti | Metriche documentate, oneste |

> La definizione precisa della ricompensa **non** si fissa adesso: si decide quando i dati reali sono davanti, per non ottimizzare la metrica sbagliata. Un bambino scopre il bene e il male vivendo, non con le regole scritte prima.

---

## Cosa si mantiene dalla Fase 2

L'**occhio (l'encoder) resta invariato e congelato**. Non si ricomincia da zero: si aggiunge la testa **sopra** la stessa base. Per questo l'ordine è obbligatorio — prima vedere, poi associare.

La **libreria dei pattern** (`models/pattern_memory/`) resta e può crescere: pattern scoperti dallo storico, pattern dai libri, e — da qui in poi — pattern rafforzati dalla ricompensa.

---

## Cosa viene dopo (Stadio 3 — Contestualizzare)

Quando il predittore supera il 53% su un singolo titolo, si passa ai **settori**: capire in giornata quale settore va meglio e come i settori si trascinano tra loro, per scegliere **dove** investire. Si progetta dopo, a Fase 3 solida.

---

## Il principio che non cambia

Un passo alla volta. Si **misura prima** di aggiungere. Si scala **solo** quando funziona. E se un test torna negativo — come la sonda — lo si accetta: si è scoperta la verità **a poco prezzo**, invece di investire alla cieca. La fretta produce sistemi che *sembrano* funzionare e non funzionano.

---

*AI Market Predictor · Versione 4.0 · Fase 3 — Il Predittore (Stadio 2). Vedi anche [predittore/README.md](../../training/predittore/README.md), [come funziona l'occhio](../../training/occhio/COME_FUNZIONA_LOCCHIO.md) e la [roadmap Fase 2](Fase2_Roadmap.md).*
