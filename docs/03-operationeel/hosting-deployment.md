# CSAT-Compass — Hosting & Deployment

**Versie:** 1.0
**Laatst bijgewerkt:** 10/04/2026

**Doel:** Opties en procedures voor het intern hosten van het Streamlit-dashboard
**Type:** Deployment
**Auteur:** Danny Depecker
**Status:** Actief

**Bestandsnaam:** hosting-deployment.md
**Path:** docs/03-operationeel/

---

## Overzicht

| Optie | Type | Geschikt voor ZORGI | Complexiteit |
|---|---|:---:|---|
| A — Streamlit Community Cloud | Publieke cloud | ❌ | Laag |
| B — Interne server / VM | On-premise | ✅ | Gemiddeld |
| C — Docker container | On-premise / VM | ✅ | Gemiddeld |

---

## Optie A — Streamlit Community Cloud *(niet aanbevolen)*

- Gratis hosting via [share.streamlit.io](https://share.streamlit.io)
- Repo op GitHub koppelen → automatisch gedeployd
- App herstart bij inactiviteit

**❌ Niet geschikt voor ZORGI** — ticketingdata (SD30) is intern en confidentieel.
Dataverkeer zou via externe servers lopen; DB-connectie op `ZRG0014WI` is niet bereikbaar van buiten het netwerk.

---

## Optie B — Interne server of VM *(aanbevolen)*

De meest logische keuze gezien de interne databron (SD30, ziekenhuizen, `.env`-credentials).

### Vereisten

- Windows Server of Linux VM in het ZORGI-netwerk
- Python 3.11+
- Toegang tot `ZRG0014WI` via ODBC Driver 18

### Installatie

```powershell
# 1. Omgeving aanmaken
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. App starten (manueel testen)
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

### Als Windows-service via NSSM

```powershell
# NSSM installeren (https://nssm.cc)
nssm install CSAT-Compass "C:\..\.venv\Scripts\streamlit.exe"
nssm set CSAT-Compass AppParameters "run src/dashboard/app.py --server.port 8501"
nssm set CSAT-Compass AppDirectory "C:\pad\naar\CSAT-Compass"
nssm start CSAT-Compass
```

- App start automatisch op bij herstart van de server
- Beheerbaar via `services.msc`

### Reverse proxy (optioneel — professioneel)

- **nginx** of **IIS** als front-end op poort 80/443
- Verwijst intern door naar `localhost:8501`
- Voegt HTTPS toe via intern certificaat
- Interne URL: bijv. `http://csat.zorgi.local`

### Firewall

- Poort `8501` openzetten enkel voor intern ZORGI-netwerk
- Niet blootstellen aan internet

### Toegangs-URL's

Zodra de app draait zijn er vier niveaus, van eenvoudig naar professioneel:

| Niveau | URL | Vereiste |
|---|---|---|
| 1 — Direct via IP | `http://192.168.x.x:8501` | Niets extra — meteen werkbaar |
| 2 — Intranet DNS | `http://csat.zorgi.local:8501` | IT: A-record in interne DNS |
| 3 — Reverse proxy | `http://csat.zorgi.local` | IIS of nginx + DNS-record |
| 4 — HTTPS | `https://csat.zorgi.local` | Intern SSL-certificaat + reverse proxy |

> **Aanbeveling:** Begin met niveau 1 om te testen, vraag daarna IT een DNS-entry aan.
> Niveau 3 geeft de nettste gebruikerservaring (geen poortnummer in de URL).

#### DNS-record aanvragen bij IT

```text
Type  : A
Naam  : csat.zorgi.local
Waarde: <IP-adres van de server>
```

---

## Optie C — Docker container *(schaalbaar, clean)*

Geschikt als ZORGI al een Docker-infrastructuur heeft (bijv. op een interne VM).

### Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "src/dashboard/app.py", \
     "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose

```yaml
services:
  csat-compass:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
    restart: unless-stopped
```

```powershell
# Bouwen en starten
docker compose up -d

# Logs bekijken
docker compose logs -f
```

- `.env` wordt via `env_file` geïnjecteerd — nooit in de image bakken
- `restart: unless-stopped` zorgt voor automatische herstart

---

## Aanbeveling voor ZORGI

| Criterium | Advies |
|---|---|
| Data blijft intern | ✅ Optie B of C op interne VM |
| DB-connectie (`ZRG0014WI`) | Server moet in hetzelfde netwerk zitten als de DB |
| Beheer eenvoud | Optie B (NSSM-service) — geen extra tooling nodig |
| Schaalbaarheid / meerdere apps | Optie C (Docker) — netter op langere termijn |
| Toegang gebruikers | Intern URL via DNS: `http://csat.zorgi.local` |
| Beveiliging | Geen publieke blootstelling — intranet only |

### Volgende stappen

- [ ] Beschikbare interne server/VM identificeren (IT aanvragen)
- [ ] Netwerktoegang `ZRG0014WI` vanop de server verifiëren
- [ ] ODBC Driver 18 installeren op de server
- [ ] Keuze maken: NSSM (Optie B) of Docker (Optie C)
- [ ] `.env` veilig overbrengen naar de server (niet via Git)
- [ ] Interne DNS-entry aanmaken: `csat.zorgi.local`

---

## Aandachtspunten

- **`.env` nooit in Git** — credentials voor DB-verbinding zitten hierin
- **`data/` en `output/` niet deployen** — lokale werkbestanden
- **Firewall** — poort 8501 enkel intern bereikbaar houden
- **Updates** — bij nieuwe versie: `git pull` + app herstarten (of Docker image rebuilden)

---

## Versiehistorie

| Versie | Datum | Wijzigingen | Auteur |
|---|---|---|---|
| 1.0 | 10/04/2026 | Initiële versie — overgenomen vanuit WIP/hosting-opties-2026-04-07.md | Danny Depecker |
