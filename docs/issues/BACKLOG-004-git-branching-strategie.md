# BACKLOG-004 — Git Branching Strategie & Workflow

**Status:** Open
**Prioriteit:** Medium
**Aangemaakt:** 17/04/2026
**Auteur:** Danny Depecker
**Gerelateerd aan:** Versiebeheer & Git-analyse (17/04/2026)

---

## Probleemstelling

Het project werkt momenteel met een **single-branch workflow** (`master` only).
Alle wijzigingen — features, fixes, micro-tweaks — landen rechtstreeks op de
productie-branch zonder isolatie. Dit verhoogt het risico op regressies en
conflicten bij parallelle ontwikkeling binnen het team.

---

## Gewenste situatie

Een minimale maar formele **branch-strategie** die past bij een klein team (4 personen):

```
master          ← stabiel, alleen via PR of hotfix
  └── develop   ← integratiebranch, dagelijkse werkbasis
        └── feature/YYYY-MM-beschrijving   ← per feature/taak
        └── fix/YYYY-MM-beschrijving       ← bugfixes
hotfix/YYYY-MM-beschrijving  ← urgente fixes direct op master
```

---

## Actiepunten

- [ ] `develop`-branch aanmaken vanuit huidige `master`
- [ ] Teamafspraak documenteren: wanneer feature-branch, wanneer direct op develop
- [ ] Squash-strategie bepalen: micro-commits bundelen vóór merge naar develop
- [ ] Commit-richtlijn uitbreiden: `chore`-categorie voor niet-functionele aanpassingen
  (opmaak, spacing, stijl) — patch-versie NIET incrementeren voor chore-only commits
- [ ] `/git`-workflow in `copilot-instructions.md` uitbreiden met branch-bewustzijn
  (stap: detecteer huidige branch, waarschuw bij directe push naar master)
- [ ] Documenteer rollback-procedure in `docs/03-operationeel/operations-runbook.md`

---

## Overwegingen

- Team is klein (4 personen) — GitHub Flow (feature → master via PR) is eenvoudiger
  dan volledige Git Flow; evaluate beide opties bij implementatie
- Squash commits: gebruik `git rebase -i --autosquash` voor iteratieve correcties
  vóór merge — behoudt leesbare history zonder verlies van details
- Versie-semantiek: patch-versies enkel voor functionele bugfixes/kleine features;
  `chore`-commits bundelen zonder versie-increment

---

## Referentie

Zie versiebeheer-analyse van 17/04/2026 (Prioriteit 2 — branching & squash-strategie).
