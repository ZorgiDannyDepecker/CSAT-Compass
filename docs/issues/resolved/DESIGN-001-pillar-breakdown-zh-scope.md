# DESIGN-001 — Scope pijler-breakdown tabel (Tab 5): 107 vs 83 ZH

**Status:** Gesloten — bewuste ontwerpkeuze
**Prioriteit:** —
**Aangemaakt:** 23/04/2026
**Gesloten:** 23/04/2026
**Context:** Sessie Fase 6 extra's — ZORGI pijler-breakdown

---

## Vastgesteld verschil

Bij de introductie van de pijler-breakdown tabel (Tab 5, sectie H) werd vastgesteld:

- **Volledig ziekenhuizenoverzicht** (Tab 5, bovenste tabel): **107 ZH**
- **Pijler-breakdown tabel** (Tab 5, sectie H): **83 ZH**

Het verschil bedraagt **24 ZH**.

---

## Oorzaak

De pijler-breakdown wordt opgebouwd via `_zh_pillar_tks` in `main()` van `app.py`.
Deze dictionary wordt enkel gevuld voor ZH waarbij:

```python
if _hc.current_score is None or _hc.current_total == 0:
    continue
```

ZH met **geen tickets in 2026** (enkel aanwezig in de 2025-baseline) worden
overgeslagen en verschijnen dus niet in de pijler-breakdown.

Het volledig ZH-overzicht wordt gevuld vanuit `data.hospital_comparison`
(ZORGI EvolutionAnalyser), dat ook baseline-only ZH omvat.

---

## Beslissing

**Optie B gekozen:** de 24 ZH zonder 2026-tickets worden **niet** getoond in de
pijler-breakdown tabel.

### Motivatie

- Een pijler-breakdown zonder 2026-data biedt geen informatieve waarde voor de gebruiker.
- Lege rijen (`—` in alle pijlerkolommen) creëren visuele ruis in een tabel die
  bedoeld is als actie-instrument.
- De 107 ZH in het volledig overzicht bieden reeds het volledige historisch beeld.
- De tabelkop vermeldt expliciet het huidig jaar (`— 2026`) als context.

---

## Documentatie in code

Zie commentaar in `src/dashboard/app.py` bij declaratie van `_zh_pillar_tks`:

```python
# Ontwerpkeuze (23/04/2026): enkel ZH met current_total > 0 worden opgenomen.
# ZH die uitsluitend in de 2025-baseline aanwezig zijn (geen 2026-tickets) worden
# bewust weggelaten. Gevolg: pijler-breakdown (Tab 5) toont minder ZH dan het
# volledig ziekenhuizenoverzicht (Tab 5 bovenste tabel). Dit is GEEN bug.
```

---

## Gerelateerde bestanden

| Bestand | Rol |
|---|---|
| `src/dashboard/app.py` | Bouwt `_zh_pillar_tks` op — filter op `current_total > 0` |
| `src/csat/core/exporters/dashboard_exporter.py` | `hospital_pillar_matrix` veld op `DashboardData` |
