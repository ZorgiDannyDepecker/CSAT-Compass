"""
CSAT-Compass — Snelle preview van de EvolutionAnalyser output.

Toont alle berekende metrics van de EvolutionAnalyser in leesbaar formaat
in de terminal — zonder templates of outputbestanden (Fase 3c).

Gebruik:
    python WIP/preview_evolution.py
    python WIP/preview_evolution.py --pillar care
    python WIP/preview_evolution.py --baseline 2025-01 2025-12 --current 2026-01 2026-03
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from csat.config.settings import CSV_FALLBACK_PATH, DB_CONN, LOG_PATH  # noqa: E402
from csat.core.analysers.evolution_analyser import EvolutionAnalyser  # noqa: E402
from csat.core.analysers.evolution_result import EvolutionResult, KpiStatus  # noqa: E402
from csat.core.loaders import get_loader  # noqa: E402
from csat.utils.date_utils import parse_period  # noqa: E402
from csat.utils.logger import setup_logger  # noqa: E402

# Kleuren voor terminal output
_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_CYAN = "\033[36m"
_GREY = "\033[90m"


def _kleur_status(status: KpiStatus) -> str:
    kleuren = {
        KpiStatus.OK: f"{_GREEN}✅ OK{_RESET}",
        KpiStatus.WARNING: f"{_YELLOW}⚠️  Aandacht{_RESET}",
        KpiStatus.AT_RISK: f"{_RED}🔴 Risico{_RESET}",
        KpiStatus.UNKNOWN: f"{_GREY}⏳ Onbekend{_RESET}",
    }
    return kleuren.get(status, str(status))


def _periods_range(from_p: str, to_p: str) -> list[str]:
    """Genereer lijst van periodes tussen from_p en to_p (inclusief)."""
    fy, fm = parse_period(from_p)
    ty, tm = parse_period(to_p)
    result = []
    y, m = fy, fm
    while (y, m) <= (ty, tm):
        result.append(f"{y}-{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return result


def druk_resultaat(r: EvolutionResult) -> None:
    """Druk het volledige EvolutionResult af in leesbaar formaat."""
    lijn = "─" * 60

    print(f"\n{_BOLD}{_CYAN}{'═' * 60}{_RESET}")
    print(f"{_BOLD}{_CYAN}  CSAT-Compass — Evolutie-analyse{_RESET}")
    print(f"{_BOLD}{_CYAN}  Pijler: {r.pillar.upper()}  |  {r.baseline_label} → {r.current_label}{_RESET}")
    print(f"{_BOLD}{_CYAN}{'═' * 60}{_RESET}\n")

    # --- Kerncijfers ---
    print(f"{_BOLD}1. Kerncijfers{_RESET}")
    print(lijn)
    delta_kleur = _GREEN if r.delta_avg_score >= 0 else _RED
    print(f"  Tickets         : {r.baseline_total:>6,} baseline  →  {r.current_total:>6,} huidig")
    print(f"  Gem. score      : {r.baseline_avg_score:>6.2f}           →  {r.current_avg_score:>6.2f}   (delta: {delta_kleur}{r.delta_avg_score:+.2f}{_RESET})")
    print(f"  % Positief ≥ 4  : {r.baseline_pct_positive:>5.1f}%          →  {r.current_pct_positive:>5.1f}%")
    print(f"  % Negatief ≤ 2  : {r.baseline_pct_negative:>5.1f}%          →  {r.current_pct_negative:>5.1f}%")
    print(f"  HC-ratio        : {r.baseline_hc_ratio:>5.1f}%          →  {r.current_hc_ratio:>5.1f}%")
    print(f"  Responstijd (d) : {r.baseline_avg_response_days:>5.1f}           →  {r.current_avg_response_days:>5.1f}")
    print(f"  Ziekenhuizen    : {r.baseline_n_hospitals:>6}           →  {r.current_n_hospitals:>6}")

    # --- KPI status ---
    print(f"\n{_BOLD}2. KPI-status{_RESET}")
    print(lijn)
    labels = {
        "avg_score_baseline": "Gem. score baseline",
        "avg_score_current": "Gem. score huidig",
        "high_critical_baseline": "HC-ratio baseline",
        "high_critical_current": "HC-ratio huidig",
        "trend": "Trend overall",
    }
    for key, label in labels.items():
        status = r.kpi_status.get(key, KpiStatus.UNKNOWN)
        print(f"  {label:<25}: {_kleur_status(status)}")

    # --- Trend ---
    print(f"\n{_BOLD}3. Trend classificatie{_RESET}")
    print(lijn)
    struct = f"{_GREEN}Structureel{_RESET}" if r.trend_is_structural else f"{_YELLOW}Tijdelijk / onduidelijk{_RESET}"
    breedte_kleur = {"breed": _GREEN, "beperkt": _RED, "gemengd": _YELLOW}
    bk = breedte_kleur.get(r.trend_breadth, _RESET)
    print(f"  Structureel     : {struct}")
    print(f"  Breedte         : {bk}{r.trend_breadth.capitalize()}{_RESET}")

    # --- Maandelijkse tijdlijn ---
    print(f"\n{_BOLD}4. Maandelijkse tijdlijn{_RESET}")
    print(lijn)
    print(f"  {'Periode':<10} {'Fase':<10} {'Tickets':>8} {'Gem. score':>12} {'% Negatief':>12}")
    print(f"  {'-'*10} {'-'*10} {'-'*8} {'-'*12} {'-'*12}")
    for dp in r.monthly_timeline:
        score_str = f"{dp.avg_score:.2f}" if dp.avg_score > 0 else "  —"
        print(f"  {dp.period:<10} {dp.fase:<10} {dp.total_tickets:>8} {score_str:>12} {dp.pct_negative:>11.1f}%")

    # --- Ziekenhuizen ---
    print(f"\n{_BOLD}5. Ziekenhuisvergelijking{_RESET}")
    print(lijn)
    print(f"  {'Ziekenhuis':<30} {'Baseline':>10} {'Huidig':>10} {'Delta':>8}")
    print(f"  {'-'*30} {'-'*10} {'-'*10} {'-'*8}")
    for h in sorted(r.hospital_comparison, key=lambda x: x.hospital):
        b = f"{h.baseline_score:.2f}" if h.baseline_score > 0 else "    —"
        c = f"{h.current_score:.2f}" if h.current_score is not None else "    —"
        if h.current_score is not None and h.baseline_score > 0:
            delta = h.current_score - h.baseline_score
            dk = _GREEN if delta >= 0 else _RED
            d = f"{dk}{delta:+.2f}{_RESET}"
        else:
            d = "    —"
        print(f"  {h.hospital:<30} {b:>10} {c:>10} {d:>8}")
    if r.hospitals_disappeared:
        print(f"\n  {_YELLOW}↓ Verdwenen in huidig  : {', '.join(r.hospitals_disappeared)}{_RESET}")
    if r.hospitals_new:
        print(f"  {_GREEN}↑ Nieuw in huidig      : {', '.join(r.hospitals_new)}{_RESET}")

    # --- Issue types ---
    print(f"\n{_BOLD}6. Vergelijking per issue type{_RESET}")
    print(lijn)
    print(f"  {'Type':<20} {'B-score':>8} {'B-neg%':>8} {'C-score':>8} {'C-neg%':>8}")
    print(f"  {'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for it in r.by_issue_type:
        bs = f"{it.baseline_score:.2f}" if it.baseline_score > 0 else "    —"
        cs = f"{it.current_score:.2f}" if it.current_score > 0 else "    —"
        print(f"  {it.issue_type:<20} {bs:>8} {it.baseline_pct_neg:>7.1f}% {cs:>8} {it.current_pct_neg:>7.1f}%")

    # --- Thema's ---
    if r.negative_themes:
        print(f"\n{_BOLD}7. Negatieve feedbackthema's{_RESET}")
        print(lijn)
        status_icons = {"OPGELOST": f"{_GREEN}✅ OPGELOST{_RESET}", "NOG_AANWEZIG": f"{_YELLOW}⚠️  NOG AANWEZIG{_RESET}", "NIEUW": f"{_RED}🔴 NIEUW{_RESET}"}
        print(f"  {'Thema':<20} {'Baseline':>10} {'Huidig':>10}  Status")
        print(f"  {'-'*20} {'-'*10} {'-'*10}  {'-'*15}")
        for t in r.negative_themes:
            icon = status_icons.get(t.status, t.status)
            print(f"  {t.theme_key:<20} {t.pct_baseline:>9.1f}% {t.pct_current:>9.1f}%  {icon}")
    else:
        print(f"\n{_GREY}  Geen negatieve feedbackthema's gedetecteerd.{_RESET}")

    # --- Responstijd per score ---
    if r.response_time_by_score:
        print(f"\n{_BOLD}8. Responstijd per score-niveau{_RESET}")
        print(lijn)
        print(f"  {'Score':<8} {'Baseline (d)':>14} {'Huidig (d)':>12}")
        print(f"  {'-'*8} {'-'*14} {'-'*12}")
        for score in sorted(r.response_time_by_score):
            row = r.response_time_by_score[score]
            b = f"{row.baseline_days:.1f}" if row.baseline_days is not None else "—"
            c = f"{row.current_days:.1f}" if row.current_days is not None else "—"
            print(f"  {'★' * score + '☆' * (5 - score):<8} {b:>14} {c:>12}")

    print(f"\n{_GREY}{'─' * 60}{_RESET}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview EvolutionAnalyser output")
    parser.add_argument("--pillar", default="pharma",
                        choices=["pharma", "care", "care_admin", "erp4hc", "zorgi"])
    parser.add_argument("--baseline", nargs=2, metavar=("VAN", "TOT"),
                        default=["2025-01", "2025-12"],
                        help="Baseline periode: VAN TOT (bv. 2025-01 2025-12)")
    parser.add_argument("--current", nargs=2, metavar=("VAN", "TOT"),
                        default=None,
                        help="Huidige periode: VAN TOT (bv. 2026-01 2026-03)")
    args = parser.parse_args()

    setup_logger(LOG_PATH)

    # Data laden
    loader = get_loader(DB_CONN, CSV_FALLBACK_PATH)
    df = loader.load()

    # Periodes opbouwen
    baseline_periods = _periods_range(args.baseline[0], args.baseline[1])
    if args.current:
        current_periods = _periods_range(args.current[0], args.current[1])
    else:
        # Automatisch: lopend jaar t/m vorige maand
        from csat.utils.date_utils import today_period, previous_period  # noqa: PLC0415
        current_end = previous_period(today_period())
        current_year = current_end[:4]
        current_periods = _periods_range(f"{current_year}-01", current_end)

    print(f"\n{_GREY}Baseline : {baseline_periods[0]} → {baseline_periods[-1]} ({len(baseline_periods)} maanden){_RESET}")
    print(f"{_GREY}Huidig   : {current_periods[0]} → {current_periods[-1]} ({len(current_periods)} maanden){_RESET}")

    # Analyse
    analyser = EvolutionAnalyser(df, pillar_key=args.pillar)
    result = analyser.analyse(baseline_periods, current_periods)

    druk_resultaat(result)


if __name__ == "__main__":
    main()

