# 🔗 Analyse copilot-instructions.md — Gemeenschappelijke secties

**Datum:** 24/03/2026
**Auteur:** Danny Depecker
**Bron:** Q&A-Lab + Scripting + CSAT-Compass (alle drie geanalyseerd)
**Status:** 📊 Analyse — input voor PHARMA-Conventions

---

## ✅ Volledig identieke secties (alle drie projecten)

De onderstaande secties zijn **woord voor woord identiek** in Q&A-Lab, Scripting én CSAT-Compass.
Dit zijn de ideale kandidaten voor een gedeeld `pharma/copilot-base.instructions.md`.

---

### 1 — Language Preference

Respond always in Dutch (Nederlands), regardless of the input language used in questions or code comments.

---

### 2 — User Information

- **Name:** Danny Depecker
- **Role:** Senior Advisor
- **Company:** ZORGI
- **Department:** PHARMA

---

### 3 — User Role Details

Identiek in alle drie projecten — Senior Advisor, hospital software, PHARMA pillar,
strategic projects en technical guidance.

---

### 4 — Abbreviations

- **GHC** = GitHub Copilot
- **PC2025** = PyCharm 2025.3

---

### 5 — User Interaction Preferences

De volgende subsecties zijn identiek in **alle drie** projecten:

| Subsectie | Status |
|---|---|
| Automatic Monitoring | ✅ Identiek |
| Terminal Command Efficiency | ✅ Identiek |
| Terminal Feedback | ✅ Identiek |
| Git Operations — basis | ✅ Identiek |
| Advice vs Action Mode | ✅ Identiek |

> ⚠️ Git Operations — `--no-pager` is identiek in Scripting + CSAT maar ontbreekt in Q&A-Lab.
> Zie afwijkingenrapport sectie 2.

---

### 6 — Prompt Quality Analysis

Volledig identiek in alle drie projecten — inclusief de ⚠️-template met
Duidelijkheid / Volledigheid / Belangrijkheid en de Q/MCQ shortcuts.

---

### 7 — Platform & Localization

Identiek in alle drie:
- Dutch Windows UI labels
- PyCharm in English
- Combinatieregel: NL uitleg + EN PyCharm labels

---

### 8 — File Search Preferences — kern

Identiek uitgesloten mappen in alle drie:
`.idea`, `.github`, `.venv`, `.git`, `node_modules`, `__pycache__`

> ⚠️ CSAT-Compass voegt twee extra exclusies toe: `data/` en `output/`.
> Zie afwijkingenrapport sectie 5.

---

### 9 — Terminal Command Output Formatting

Identiek in alle drie:
- Command block: ```powershell / ```bash met "Command om uit te voeren:" header
- Output block: ```text met "Verwachte terminal output:" header
- PowerShell syntax voor Windows (pwsh.exe)

---

### 10 — /pdf commando

Identiek in alle drie — zelfde Python-script, zelfde paden, zelfde uitvoeringsregels.

```
python "C:\Users\danndepe\Documents\AI\Q&A-Lab\code\md_to_pdf.py" --batch "C:\Users\danndepe\Documents\Convertiemap\IN" "C:\Users\danndepe\Documents\Convertiemap\OUT" -p -d
```

---

### 11 — /advies commando

Identiek in alle drie — MCQ-aanpak, één vraag per keer, **(advies)** markering, max 10 vragen.

---

## 📌 Aanbeveling

Bovenstaande 11 secties vormen de **stabiele kern** die zonder aanpassingen naar
`PHARMA-Conventions\pharma\copilot-base.instructions.md` kan worden overgeheveld.

Elk project importeert of includet dit basisbestand en voegt enkel projectspecifieke
secties toe in de eigen `copilot-instructions.md`.

Secties die in 2 van de 3 projecten aanwezig zijn (Number Formatting, `--no-pager`,
3-Layer principe, /GIT, /cve) worden behandeld in het afwijkingenrapport met een
aanbeveling om ze alsnog te generaliseren.

---

*Danny Depecker — 24/03/2026*
