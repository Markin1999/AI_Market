# predittore/ — IA #2: imparare a PREVEDERE (Stadio 2)

> **Stato: DA COSTRUIRE.** Questa è la **seconda IA** del progetto, **separata** dall'occhio. L'occhio (in [../occhio/](../occhio/)) sa *vedere* le forme; il predittore impara a *prevedere* cosa succede dopo. Roadmap dettagliata: [Fase3_Roadmap.md](../../Regole/Roadmap%20delle%20fasi/Fase3_Roadmap.md).

---

## Cosa fa (e cosa la distingue dall'occhio)

L'occhio è **congelato e finito**: trasforma un giorno in una firma + una forma. Il predittore si mette **sopra** l'occhio e risponde a: *"vista questa situazione, il prezzo salirà o scenderà nelle prossime candele?"*

| | Occhio (IA #1) | Predittore (IA #2) |
|---|---|---|
| Compito | **vedere** le forme | **prevedere** su/giù |
| Stato | fatto, validato | da addestrare |
| Impara da | ricostruzione (ricopiare) | **ricompensa** (giusto / sbagliato) |
| Cartella | [../occhio/](../occhio/) | questa |

L'occhio **non si ritocca**: il predittore si costruisce sopra la stessa base. Non si può prevedere senza prima saper vedere.

---

## Cosa abbiamo già imparato — la sonda

Prima di costruire, abbiamo misurato il **pavimento** con [sonda_predittiva.py](sonda_predittiva.py):

> La **forma da sola** (1 numero su 164) **non** prevede la direzione: ~50%, come tirare una moneta. Nessun vantaggio sul baseline.

**Lezione (guida tutta la Fase 3):** il predittore **non può** usare solo la forma grezza. Deve usare la **firma ricca** (32 numeri) **+ i 45 indicatori**, e una **testa che impara** — non una semplice media. (Dettagli: [Fase3_Roadmap.md](../../Regole/Roadmap%20delle%20fasi/Fase3_Roadmap.md).)

---

## Cosa userà

- **Ingressi:** la firma dell'occhio (32 numeri) **+ i 45 indicatori** (per qualificare la situazione)
- **Testa:** una rete che **impara** (prima supervisionata, poi con ricompensa)
- **Bersaglio:** la direzione del prezzo nelle prossime candele
- **Soglia di successo:** accuracy direzionale **> 53% out-of-sample** (sul futuro mai visto)
- **Sempre:** addestramento sul passato, verifica sul futuro, e il **log** (in `logs/`)

---

## File

| File | Cosa fa |
|---|---|
| `sonda_predittiva.py` | La **sonda diagnostica**: ha misurato che la forma da sola non basta (≈50%). È il **baseline da battere**. Scrive in `logs/probe.log`. |
| `train_predittore.py` | *(da creare)* il ciclo di addestramento della testa decisionale. |
| `__init__.py` | marker di pacchetto. Non si tocca. |

---

## Collegamenti

- Come funziona l'occhio (la base) → [../occhio/COME_FUNZIONA_LOCCHIO.md](../occhio/COME_FUNZIONA_LOCCHIO.md)
- Roadmap della Fase 3 → [Fase3_Roadmap.md](../../Regole/Roadmap%20delle%20fasi/Fase3_Roadmap.md)
- Visione d'insieme del training → [../README.md](../README.md)

---

*AI Market Predictor · Fase 3 · Stadio 2 — Associare. La seconda IA, da costruire sopra l'occhio.*
