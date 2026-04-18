---
description: "Controleer testafdoendheid en detecteer hiaten voor recente implementaties in CSAT-Compass"
name: "test-coverage-gap-review"
agent: "github-copilot"
---

# CSAT-Compass - Test Coverage & Gap Review

**Versie:** 1.2
**Laatst bijgewerkt:** 18/04/2026

**Doel:** Systematische controle van testafdoendheid en detectie van hiaten voor implementaties
van de afgelopen twee weken
**Type:** Guide
**Auteur:** Danny Depecker + GHC
**Status:** Approved

**Bestandsnaam:** test-coverage-gap-review.md
**Path:** .github/prompts/

---

## Doel & Context

Deze prompt voert een gestructureerde test coverage review uit op het CSAT-Compass project.
De focus ligt op implementaties die **in de afgelopen twee weken** zijn toegevoegd of gewijzigd.

**Wanneer gebruiken:**

- Na een implementatiesprint om testdekking te verificeren
- Voor een release om regressierisico's in kaart te brengen
- Periodiek (tweewekelijks) als kwaliteitscheck

---

## Framework: Rol — Taak — Formaat (RTF)

### R — Rol

Je bent een ervaren software test engineer en code reviewer met sterke kennis van:

- Unit tests, integratietests en regressietesting
- Python `pytest`-ecosysteem (fixtures, parametrize, mocks)
- Code coverage analyse (`coverage.py`, `htmlcov/`)
- Enterprise kwaliteitsstandaarden in een professionele omgeving

---

### T — Taak

#### Stap 1: Identificeer recente wijzigingen

Analyseer de codewijzigingen van de afgelopen twee weken:

```powershell
# Gewijzigde bestanden in de afgelopen 14 dagen
git --no-pager log --since="14 days ago" --name-only --pretty=format: | Sort-Object -Unique
```

Focus op bestanden in:

- `src/` — Python broncode (analyse, rapportage, visualisatie)
- `tests/` — Bestaande testsuites

#### Stap 1b: Controleer bestandsdekking (structureel)

Voer altijd een structurele scan uit: welke `src/`-bestanden hebben **helemaal geen** bijbehorend testbestand?

```powershell
# Vergelijk src-bestanden met testbestanden op bestandsnaam
$src   = Get-ChildItem src/ -Recurse -Filter "*.py" |
         Where-Object { $_.Name -ne "__init__.py" } |
         ForEach-Object { $_.Name }
$tests = Get-ChildItem tests/ -Recurse -Filter "test_*.py" |
         ForEach-Object { $_.Name -replace "^test_", "" }

Write-Host "=== GEEN TEST ==="
$src | Where-Object { $_ -notin $tests } | Sort-Object |
    ForEach-Object { Write-Host "  $_" }
```

Beoordeel elk gevonden bestand volgens dit schema:

| Situatie | Actie |
| :--- | :--- |
| Bestand met logica, geen test | ❌ Toevoegen aan hiatenlijst |
| Indirect gedekt via bestaand testbestand | ⚠️ Vermelden als "indirect gedekt" |
| Pure dataconfiguratie (enkel dicts/constanten) | ✅ Bewust niet getest — documenteer dit |
| Thin wrapper die volledig delegeert | ✅ Bewust niet getest — documenteer dit |

#### Stap 2: Beoordeel de testdekking

Controleer voor elke gewijzigde component of gewijzigd bestand:

- Bestaat er een corresponderende testmodule in `tests/`?
- Worden alle **nieuwe functies/methoden** gedekt door minstens één test?
- Zijn er **randgevallen** (lege input, `None`, grenswaarden) getest?
- Zijn er **negatieve paden** (fouten, uitzonderingen) opgenomen?
- Geven bestaande testen **vals vertrouwen** (slagen maar dekken nieuwe logica niet)?

#### Stap 3: Analyseer het coverage rapport

Raadpleeg het meest recente coverage rapport:

```powershell
# Coverage rapport genereren (indien nog niet aanwezig)
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -q
```

- Inspecteer `htmlcov/index.html` voor een visueel overzicht
- Identificeer regels met `# pragma: no cover` — zijn die gerechtvaardigd?
- Let op modules met coverage **onder 80%** als prioritaire aandachtszone

#### Stap 4: Detecteer ontbrekende testscenario's

Controleer specifiek op:

- [ ] Happy path getest?
- [ ] Lege dataframe / lege lijst als input?
- [ ] `None`-waarden in verplichte velden?
- [ ] Foutieve datatypen (bv. string i.p.v. float)?
- [ ] Grenscondities (min/max scores, 0 tickets, 100% negatief)?
- [ ] Tweetalige output (`lang='nl'` én `lang='fr'`)?
- [ ] Gegenereerde Markdown correct gestructureerd?

#### Stap 5: Verifieer dat nieuwe testbestanden effectief op schijf staan

> ⚠️ **Valkuil:** Editors (JetBrains, VS Code) houden soms bestanden in een virtuele buffer
> zonder ze naar schijf te schrijven. Een testbestand dat niet op schijf staat wordt door
> pytest niet gevonden en levert een stille dekking-illusie op.

Controleer altijd **na het aanmaken van nieuwe testbestanden**:

```powershell
# Verifieer dat de bestanden op schijf staan
Get-ChildItem tests/ -Recurse -Filter "test_*.py" | Select-Object Name, FullName

# Draai een eerste snelle run op enkel de nieuwe bestanden
python -m pytest tests/pad/naar/test_nieuw.py --no-cov -q
```

**Wanneer een nieuw bestand aanmaken via de editor mislukt**, gebruik dan PowerShell direct:

```powershell
Set-Content -Path "tests/pad/naar/test_nieuw.py" -Value $content -Encoding UTF8
```

---

### F — Formaat

Lever het resultaat aan als een gestructureerd overzicht met **vijf** secties:

#### Sectie 1: Samenvatting (max. 5 regels)

Geef een beknopte beoordeling van de algemene testkwaliteit:
risicoscore (laag / gemiddeld / hoog), trend t.o.v. vorige review, en hoofdconclusie.

#### Sectie 2: Overzichtstabel

| Component / Bestand | Teststatus | Vastgestelde hiaten |
| :------------------ | :--------: | :------------------ |
| `src/...`           | ✅ / ⚠️ / ❌ | Beschrijving van het hiaat |

Legenda:

- ✅ **Voldoende** — alle paden afgedekt, geen kritieke hiaten
- ⚠️ **Twijfelachtig** — gedeeltelijke dekking, randgevallen ontbreken
- ❌ **Onvoldoende** — nieuwe logica niet of nauwelijks getest

#### Sectie 3: Ontbrekende testcases

Lijst van concrete testcases die moeten worden toegevoegd of uitgebreid:

- `tests/test_[module].py::test_[functie]_[scenario]` — Beschrijving
- Groepeer per module voor overzichtelijkheid

#### Sectie 4: Aanbevelingen (geprioriteerd)

| Prioriteit | Aanbeveling | Impact |
| :--------: | :---------- | :----- |
| 🔴 Hoog | Concrete actie | Regressierisico / releaseblocker |
| 🟡 Gemiddeld | Concrete actie | Kwaliteitsverbetering |
| 🟢 Laag | Concrete actie | Nice-to-have |

#### Sectie 5: Bewust niet geteste bestanden

Lijst van bestanden die **geen test nodig hebben** en waarom — zodat de volgende
reviewer niet opnieuw dezelfde analyse uitvoert:

| Bestand | Reden |
| :--- | :--- |
| `src/csat/pillars/*/analyser.py` | Thin wrapper — delegeert aan `PillarAnalyser` (getest) |
| `src/csat/pillars/*/config.py` | Pure dataconfiguratie — geen logica |
| `src/csat/utils/zorgi_theme.py` | Matplotlib-kleur/fontconstanten — geen logica |

---

## Projectspecifieke Aandachtspunten

Bij de review altijd rekening houden met CSAT-Compass-specifieke aspecten:

### Tweetaligheid

Elke generator die tekst produceert (`_generate_*` methoden) vereist tests voor:

```python
# Verplicht te testen:
result_nl = generator.methode(df, lang='nl')
result_fr = generator.methode(df, lang='fr')
assert isinstance(result_nl, str) and len(result_nl) > 0
assert isinstance(result_fr, str) and len(result_fr) > 0
```

### Lege data

Alle analyse-componenten moeten correct omgaan met lege of onvolledige datasets:

```python
# Minimale smoke test voor lege input:
df_empty = pd.DataFrame(columns=['score', 'category', ...])
result = component.analyse(df_empty)
assert result is not None  # geen crash
```

### Score-berekeningen

Verificeer dat score-berekeningen consistent zijn met de CSAT-logica:

- Scores liggen altijd in het bereik **[1.0, 5.0]**
- `pct_neg` = aandeel scores **≤ 2★**
- Gewogen gemiddelden correct berekend bij ongelijke groepsgroottes

### Pijler-wrappers en configuratiebestanden

De 5 pijlerspecifieke `analyser.py`-bestanden (`pharma/`, `care/`, `care_admin/`,
`erp4hc/`, `zorgi/`) zijn **thin wrappers** die volledig delegeren aan `PillarAnalyser`.
Ze hebben **bewust geen eigen testbestand** — dekking verloopt via `test_pillar_analyser.py`.

De bijbehorende `config.py`-bestanden bevatten enkel dataconfiguraties (dicts met
productnamen en drempelwaarden) zonder logica — ook **bewust niet getest**.

> Documenteer deze beslissing expliciet in de overzichtstabel (Sectie 2) als
> "✅ Bewust niet getest — thin wrapper / pure config" zodat de volgende reviewer
> niet opnieuw dezelfde analyse hoeft uit te voeren.

### Indirecte dekking vs. ontbrekende dekking

Sommige bestanden hebben geen eigen testbestand maar zijn **indirect gedekt**:

| Bestand | Gedekt door |
| :--- | :--- |
| `evolution_result.py` | `test_evolution_analyser.py` — alle dataklassen uitgebreid getest |
| `csv_loader.py` | `test_loaders.py` → `TestCsvLoader` + `TestCsvLoaderExtra` |
| `sql_loader.py` | `test_loaders.py` → `TestSqlLoaderMocked` |
| `base_loader.py` | `test_loaders.py` → `TestBaseLoaderValidatie` |

Controleer bij twijfel de coverage via:

```powershell
python -m pytest tests/ --cov=src/csat/core/loaders --cov-report=term-missing --no-cov-on-fail -q
```

### Abstracte basisklassen

Abstracte klassen (`BaseAnalyser`, `BaseLoader`) kunnen niet direct geïnstantieerd worden.
Test ze altijd via een **minimale concrete subklasse**:

```python
class ConcreteAnalyser(BaseAnalyser):
    def analyse(self, period: str) -> KpiResult:
        return KpiResult(period=period, pillar="test")
```

Dit patroon is toegepast in `test_base_analyser.py` en dient als referentie.

---

## Bronnen & Referenties

- `tests/` — Bestaande testsuites
- `htmlcov/index.html` — Coverage rapport (meest recent)
- `coverage.xml` — Machine-leesbaar coverage rapport
- `src/` — Python broncode
- `docs/CHANGELOG.md` — Recente wijzigingen

---

## Verwante Commando's

```powershell
# Alle testen uitvoeren met coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Alleen gefaalde testen herhalen
python -m pytest tests/ --lf -v

# Coverage voor specifieke module
python -m pytest tests/test_insights.py -v --cov=src/csat/core/insights
```

> ✅ **Tip:** Gebruik `/pytest` om testen te starten via de geïntegreerde GHC-flow.

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
| ------ | ---------- | ----------- | ------ |
| 1.0 | 18/04/2026 | Initiële versie — experimentele YAML-structuur omgezet naar projectstandaard (md-style-guide v4.4 + summarize-week.md als referentie) | Danny Depecker + GHC |
| 1.1 | 18/04/2026 | Projectspecifieke aandachtspunten toegevoegd: tweetaligheid, lege data, score-validatie | Danny Depecker + GHC |
| 1.2 | 18/04/2026 | Stap 1b toegevoegd (bestandsdekking-scan via PowerShell); Stap 5 toegevoegd (verificatie testbestanden op schijf + valkuil editor-buffer); F-sectie uitgebreid met Sectie 5 (bewust niet geteste bestanden); Projectspecifieke aandachtspunten uitgebreid: pijler-wrappers, indirecte dekking, abstracte basisklassen | Danny Depecker + GHC |
