"""
InsightsGenerator voor CSAT-Compass — Fase 3g.

Regelgebaseerde interpretatie-engine: zet EvolutionResult om naar narratieve
secties voor het evolutierapport. Gedeeld tussen evolutie- en maandrapport
(beslissing 7 fase3f).

Architectuur (fase3f §Laag 3):
- Ontvangt een EvolutionResult (data-laag)
- Produceert een InsightsBundle (narratieve laag)
- Zinsvariatie via i18n-bibliotheek (nl.json / fr.json) + random.Random(seed)
- Ernst-afhankelijke woordkeuze via SEVERITY_THRESHOLDS
- Connector-logica voor vloeiende proza

Beslissingen:
- beslissing 1:  Volledig regelgebaseerd — geen LLM
- beslissing 7:  Gedeeld tussen evolutie + maandrapport
- beslissing 8:  Visuele analyse per subplot
- beslissing 9:  Aanbevelingen met impact / tijdlijn / eigenaar
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from csat.core.analysers.evolution_result import EvolutionResult

# ---------------------------------------------------------------------------
# Uitvoerdataklassen (insights-laag — niet in evolution_result.py)
# ---------------------------------------------------------------------------


@dataclass
class CriticalFinding:
    """Kritieke bevinding voor het rapport (3-5 stuks)."""

    title: str
    description: str
    severity: str = "medium"  # "hoog" | "medium" | "laag"
    causal_factor: str = ""


@dataclass
class PositiveDevelopment:
    """Positieve ontwikkeling om expliciet te benoemen."""

    title: str
    description: str


@dataclass
class Recommendation:
    """Strategische aanbeveling met impact, tijdlijn en eigenaar (beslissing 9)."""

    title: str
    description: str
    expected_impact: str
    timeline: str  # "kort" | "middellang" | "lang"
    owner: str  # "Service Manager" | "Team Lead" | ...
    priority: str  # "hoog" | "midden" | "laag"


@dataclass
class FollowUpAction:
    """Follow-up actie per tijdshorizon."""

    action: str
    horizon: str  # "kort" | "middellang" | "lang"
    owner: str = ""


@dataclass
class VisualAnalysis:
    """Narratieve beschrijving per subplot van de evolutievisualisatie (beslissing 8)."""

    subplot1_scoretrend: str = ""
    subplot2_volume: str = ""
    subplot3_priority: str = ""
    subplot4_hospitals: str = ""


@dataclass
class InsightsBundle:
    """Geaggregeerde output van InsightsGenerator.generate()."""

    executive_summary: str = ""
    critical_findings: list[CriticalFinding] = field(default_factory=list)
    positive_developments: list[PositiveDevelopment] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    follow_up_actions: list[FollowUpAction] = field(default_factory=list)
    visual_analysis: VisualAnalysis = field(default_factory=VisualAnalysis)
    turning_point_analysis: str = ""


# ---------------------------------------------------------------------------
# Ernst-drempels (fase3f §Bouwblok 2) — configureerbaar per pijler
# ---------------------------------------------------------------------------

SEVERITY_THRESHOLDS: dict[str, dict[str, float]] = {
    "score_delta": {"licht": 0.10, "matig": 0.30},  # abs(delta)
    "hc_ratio_delta": {"licht": 2.0, "matig": 5.0},  # procentpunten
    "response_days": {"licht": 2.0, "matig": 5.0},  # dagen verschil
    "pct_negative": {"licht": 5.0, "matig": 10.0},  # absolute waarde
}


def _fmt_nl(value: float, decimals: int = 1) -> str:
    """Formatteer een getal in ZORGI-notatie (punt = duizendtal, komma = decimaal)."""
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# InsightsGenerator
# ---------------------------------------------------------------------------


class InsightsGenerator:
    """
    Regelgebaseerde interpretatie-engine voor CSAT-rapporten.

    Ontvangt een EvolutionResult en produceert een InsightsBundle met alle
    narratieve secties. Zinsvariatie via i18n-bibliotheek met random.Random(seed)
    voor reproduceerbaarheid.

    Args:
        i18n: Vertaalwoordenboek (nl.json of fr.json) — volledig geladen dict.
        lang: Taalcode ("nl" of "fr").
        seed: Optionele seed voor zinsvariatie (None = niet-deterministisch).
              Gebruik de rapportdatum als seed voor reproduceerbaarheid.
    """

    def __init__(self, i18n: dict, lang: str = "nl", seed: int | None = None) -> None:
        self._t = i18n
        self._lang = lang
        self._rng = random.Random(seed)  # noqa: S311 — zinsvariatie, geen cryptografie

    # ------------------------------------------------------------------
    # Publieke interface
    # ------------------------------------------------------------------

    def generate(self, result: EvolutionResult) -> InsightsBundle:
        """
        Genereer alle narratieve inzichten vanuit een EvolutionResult.

        Args:
            result: Voltooide EvolutionResult van EvolutionAnalyser.analyse().

        Returns:
            InsightsBundle met executive_summary, findings, recommendations etc.
        """
        return InsightsBundle(
            executive_summary=self._build_executive_summary(result),
            critical_findings=self._build_critical_findings(result)[:5],
            positive_developments=self._build_positive_developments(result),
            recommendations=self._build_recommendations(result),
            follow_up_actions=self._build_follow_up_actions(result),
            visual_analysis=self._build_visual_analysis(result),
            turning_point_analysis=self._build_turning_point_analysis(result),
        )

    # ------------------------------------------------------------------
    # Publieke hulpfuncties (ook bruikbaar in maandrapport)
    # ------------------------------------------------------------------

    def classify_severity(self, abs_delta: float, metric: str) -> str:
        """
        Classificeer de ernst van een afwijking.

        Args:
            abs_delta: Absolute waarde van de delta.
            metric:    Sleutel in SEVERITY_THRESHOLDS (bv. "score_delta").

        Returns:
            "licht" | "matig" | "significant"
        """
        thresholds = SEVERITY_THRESHOLDS.get(metric, {"licht": 0.1, "matig": 0.3})
        if abs_delta < thresholds["licht"]:
            return "licht"
        elif abs_delta < thresholds["matig"]:
            return "matig"
        return "significant"

    # ------------------------------------------------------------------
    # Intern — executive summary (KRITIEK gap)
    # ------------------------------------------------------------------

    def _build_executive_summary(self, result: EvolutionResult) -> str:  # noqa: C901
        """
        Bouw een managementgerichte executive summary op.

        Bevat: score-observatie met ernst-afhankelijke woordkeuze,
        scoreverdeling-narratief, correlatie-inzicht (indien beschikbaar),
        en slotboodschap.
        """
        parts: list[str] = []
        delta = result.delta_avg_score

        # 1. Score-observatie met ernst-afhankelijke woordkeuze
        if abs(delta) < 0.05:
            score_text = self._pick(
                self._get_i18n("insights.score_stable"),
                current=_fmt_nl(result.current_avg_score, 2),
            )
        elif delta > 0:
            severity = self.classify_severity(delta, "score_delta")
            score_text = self._pick(
                self._get_i18n(f"insights.score_increase.{severity}"),
                baseline=_fmt_nl(result.baseline_avg_score, 2),
                current=_fmt_nl(result.current_avg_score, 2),
            )
        else:
            severity = self.classify_severity(abs(delta), "score_delta")
            score_text = self._pick(
                self._get_i18n(f"insights.score_decline.{severity}"),
                baseline=_fmt_nl(result.baseline_avg_score, 2),
                current=_fmt_nl(result.current_avg_score, 2),
            )
        parts.append(score_text)

        # 2. Scoreverdeling-narratief (beslissing 12)
        if result.score_distribution_current and result.score_distribution_current.narrative:
            parts.append(result.score_distribution_current.narrative)

        # 3. Contextuele nuancering: kleine daling maar positief % stabiel
        if delta < 0 and abs(delta) < 0.15 and result.current_pct_positive > 75.0:
            nuance = self._pick(
                self._get_i18n("insights.nuance.stable_positive"),
                pct=_fmt_nl(result.current_pct_positive, 1),
            )
            if nuance and parts:
                connector = self._pick(self._get_i18n("insights.connectors.contrast"))
                parts[-1] = f"{parts[-1]} {connector} {nuance[0].lower()}{nuance[1:]}"

        # 4. Responstijd-correlatie (indien beschikbaar — KRITIEK gap)
        rti = result.response_time_insight
        if rti and rti.correlation_score is not None:
            r = rti.correlation_score
            if r > 0.1:
                corr_text = self._pick(
                    self._get_i18n("insights.correlation.positive"),
                    r=_fmt_nl(r, 3),
                )
            elif r < -0.1:
                corr_text = self._pick(
                    self._get_i18n("insights.correlation.negative"),
                    r=_fmt_nl(r, 3),
                )
            else:
                corr_text = self._pick(
                    self._get_i18n("insights.correlation.neutral"),
                    r=_fmt_nl(r, 3),
                )
            if corr_text:
                parts.append(corr_text)

        # 5. Slotboodschap
        if result.trend_is_structural and result.trend_breadth == "breed":
            conclusion = self._pick(self._get_i18n("insights.conclusion.structural_broad"))
        elif result.trend_is_structural:
            conclusion = self._pick(self._get_i18n("insights.conclusion.structural_limited"))
        elif delta < -0.3:
            conclusion = self._pick(self._get_i18n("insights.conclusion.declining"))
        else:
            conclusion = self._pick(self._get_i18n("insights.conclusion.stable"))

        if conclusion:
            connector = self._pick(self._get_i18n("insights.connectors.concluding"))
            parts.append(f"{connector}: {conclusion}")

        return " ".join(p for p in parts if p)

    # ------------------------------------------------------------------
    # Intern — kritieke bevindingen (KRITIEK gap)
    # ------------------------------------------------------------------

    def _build_critical_findings(self, result: EvolutionResult) -> list[CriticalFinding]:
        """
        Genereer 3-5 kritieke bevindingen met causaliteit en ernst.

        Elke bevinding bevat titel, beschrijving, ernst en causale factor.
        """
        findings: list[CriticalFinding] = []

        # Bevinding 1: Score-evolutie
        delta = result.delta_avg_score
        if abs(delta) >= 0.1:
            sev = self.classify_severity(abs(delta), "score_delta")
            direction = "gestegen" if delta > 0 else "gedaald"
            emoji = "✅" if delta > 0 else ("🔴" if sev == "significant" else "⚠️")
            findings.append(
                CriticalFinding(
                    title=f"{emoji} Scoretrend: {direction} met {_fmt_nl(abs(delta), 2)}",
                    description=(
                        f"De gemiddelde CSAT-score {direction} van "
                        f"{_fmt_nl(result.baseline_avg_score, 2)} naar "
                        f"{_fmt_nl(result.current_avg_score, 2)} "
                        f"({result.baseline_label} → {result.current_label}). "
                        f"De breedte van deze beweging is {result.trend_breadth}."
                    ),
                    severity="hoog" if sev == "significant" else sev,
                    causal_factor="Score-evolutie over analyseperiode",
                )
            )

        # Bevinding 2: Responstijd-correlatie
        rti = result.response_time_insight
        if rti and rti.correlation_score is not None and abs(rti.correlation_score) > 0.05:
            r = rti.correlation_score
            if r > 0.1:
                desc = (
                    (
                        f"Er is een positieve correlatie (r={_fmt_nl(r, 3)}) tussen "
                        f"responstijd en klanttevredenheid. Positieve scores: "
                        f"gem. {_fmt_nl(rti.avg_positive_days or 0, 1)} d | "
                        f"Negatieve scores: gem. {_fmt_nl(rti.avg_negative_days or 0, 1)} d."
                    )
                    if rti.avg_positive_days is not None and rti.avg_negative_days is not None
                    else (
                        f"Er is een positieve correlatie (r={_fmt_nl(r, 3)}) tussen "
                        f"responstijd en klanttevredenheid: snellere afhandeling gaat samen met hogere scores."
                    )
                )
                findings.append(
                    CriticalFinding(
                        title=f"⏱️ Responstijd correleert met klanttevredenheid (r={_fmt_nl(r, 3)})",
                        description=desc,
                        severity="hoog",
                        causal_factor="Responstijd is aantoonbaar gelinkt aan CSAT-score",
                    )
                )
            elif r < -0.1:
                findings.append(
                    CriticalFinding(
                        title=f"⏱️ Negatieve correlatie responstijd ↔ score (r={_fmt_nl(r, 3)})",
                        description=(
                            f"Langere responstijden gaan samen met hogere scores (r={_fmt_nl(r, 3)}). "
                            f"Mogelijke verklaring: complexere tickets vragen meer tijd maar worden positiever beoordeeld."
                        ),
                        severity="medium",
                        causal_factor="Complexe tickets correleren met hogere scores",
                    )
                )

        # Bevinding 3: Negatief % boven drempel
        if result.current_pct_negative > 10.0:
            sev = "hoog" if result.current_pct_negative > 15.0 else "medium"
            findings.append(
                CriticalFinding(
                    title=f"🔴 Negatief percentage: {_fmt_nl(result.current_pct_negative, 1)}%",
                    description=(
                        f"{_fmt_nl(result.current_pct_negative, 1)}% van de gescoorde tickets "
                        f"is negatief (≤ 2★) in {result.current_label}. "
                        f"Baseline was {_fmt_nl(result.baseline_pct_negative, 1)}%. "
                        f"Zie de negatieve feedback deep-dive voor details."
                    ),
                    severity=sev,
                    causal_factor="Hoog aandeel ontevreden klanten",
                )
            )

        # Bevinding 4: HC-ratio boven drempel
        if result.current_hc_ratio > 15.0:
            findings.append(
                CriticalFinding(
                    title=f"🔴 HC-ratio: {_fmt_nl(result.current_hc_ratio, 1)}%",
                    description=(
                        f"De High/Critical-ratio bedraagt {_fmt_nl(result.current_hc_ratio, 1)}% "
                        f"in {result.current_label} (drempel: 15%). "
                        f"Baseline: {_fmt_nl(result.baseline_hc_ratio, 1)}%."
                    ),
                    severity="hoog" if result.current_hc_ratio > 25.0 else "medium",
                    causal_factor="Verhoogd aandeel urgente tickets",
                )
            )

        # Bevinding 5: Ziekenhuisretentie onder drempel
        if result.hospital_retention_pct < 75.0 and result.hospitals_disappeared:
            n = len(result.hospitals_disappeared)
            findings.append(
                CriticalFinding(
                    title=f"🏥 Ziekenhuisretentie: {_fmt_nl(result.hospital_retention_pct, 1)}%",
                    description=(
                        f"{n} ziekenhuis{'' if n == 1 else 'en'} uit de baseline "
                        f"{'is' if n == 1 else 'zijn'} niet aanwezig in {result.current_label}: "
                        f"{', '.join(result.hospitals_disappeared)}. "
                        f"Controleer of dit data-aanlevering of stopzetting betreft."
                    ),
                    severity="hoog" if result.hospital_retention_pct < 50.0 else "medium",
                    causal_factor="Verminderde dekking of data-probleem",
                )
            )

        # Sorteer: hoog → medium → laag
        order = {"hoog": 0, "medium": 1, "laag": 2}
        findings.sort(key=lambda f: order.get(f.severity, 3))
        return findings

    # ------------------------------------------------------------------
    # Intern — positieve ontwikkelingen
    # ------------------------------------------------------------------

    def _build_positive_developments(self, result: EvolutionResult) -> list[PositiveDevelopment]:
        """Detecteer en benoem positieve ontwikkelingen."""
        devs: list[PositiveDevelopment] = []

        # Score gestegen
        if result.delta_avg_score >= 0.1:
            devs.append(
                PositiveDevelopment(
                    title="Scoreverbeter­ing t.o.v. baseline",
                    description=(
                        f"De gemiddelde CSAT-score steeg van "
                        f"{_fmt_nl(result.baseline_avg_score, 2)} naar "
                        f"{_fmt_nl(result.current_avg_score, 2)} "
                        f"(+{_fmt_nl(result.delta_avg_score, 2)})."
                    ),
                )
            )

        # % positief gestegen
        delta_pos = result.current_pct_positive - result.baseline_pct_positive
        if delta_pos >= 2.0:
            devs.append(
                PositiveDevelopment(
                    title="Stijging % positieve scores",
                    description=(
                        f"Het aandeel positieve beoordelingen (≥ 4★) nam toe van "
                        f"{_fmt_nl(result.baseline_pct_positive, 1)}% naar "
                        f"{_fmt_nl(result.current_pct_positive, 1)}% "
                        f"(+{_fmt_nl(delta_pos, 1)}pp)."
                    ),
                )
            )

        # Responstijd verbeterd
        delta_resp = result.current_avg_response_days - result.baseline_avg_response_days
        if delta_resp < -1.0:
            devs.append(
                PositiveDevelopment(
                    title="Kortere gemiddelde responstijd",
                    description=(
                        f"De gemiddelde responstijd daalde van "
                        f"{_fmt_nl(result.baseline_avg_response_days, 1)} naar "
                        f"{_fmt_nl(result.current_avg_response_days, 1)} dagen "
                        f"({_fmt_nl(delta_resp, 1)} d)."
                    ),
                )
            )

        # Opgeloste feedbackthema's
        resolved = [t for t in result.negative_themes if t.status == "OPGELOST"]
        if resolved:
            theme_names = ", ".join(t.theme_key for t in resolved)
            devs.append(
                PositiveDevelopment(
                    title=f"Opgeloste feedbackthema's ({len(resolved)})",
                    description=(
                        f"De volgende thema's waren aanwezig in de baseline maar zijn "
                        f"verdwenen in {result.current_label}: {theme_names}."
                    ),
                )
            )

        # HC-ratio verbeterd
        delta_hc = result.current_hc_ratio - result.baseline_hc_ratio
        if delta_hc < -2.0:
            devs.append(
                PositiveDevelopment(
                    title="Daling High/Critical-ratio",
                    description=(
                        f"De HC-ratio daalde van {_fmt_nl(result.baseline_hc_ratio, 1)}% "
                        f"naar {_fmt_nl(result.current_hc_ratio, 1)}% "
                        f"({_fmt_nl(delta_hc, 1)}pp)."
                    ),
                )
            )

        return devs

    # ------------------------------------------------------------------
    # Intern — strategische aanbevelingen (beslissing 9)
    # ------------------------------------------------------------------

    def _build_recommendations(self, result: EvolutionResult) -> list[Recommendation]:
        """
        Genereer geprioriteerde strategische aanbevelingen.

        Elke aanbeveling bevat impact, tijdlijn en eigenaar (beslissing 9).
        """
        recs: list[Recommendation] = []

        # Aanbeveling: responstijd optimaliseren (als correlatie > 0,1)
        rti = result.response_time_insight
        if rti and rti.correlation_score is not None and rti.correlation_score > 0.1:
            recs.append(
                Recommendation(
                    title="Responstijd optimaliseren",
                    description=(
                        f"De positieve correlatie (r={_fmt_nl(rti.correlation_score, 3)}) toont "
                        f"aan dat kortere responstijden direct bijdragen aan hogere CSAT-scores. "
                        f"Huidig gemiddelde: {_fmt_nl(result.current_avg_response_days, 1)} d."
                    ),
                    expected_impact="Verwachte scoreverbetering +0,10 tot +0,20 bij halvering responstijd",
                    timeline="kort",
                    owner="Service Manager",
                    priority="hoog",
                )
            )

        # Aanbeveling: HC-ratio verlagen
        if result.current_hc_ratio > 15.0:
            recs.append(
                Recommendation(
                    title="HC-ratio terugdringen",
                    description=(
                        f"De High/Critical-ratio ({_fmt_nl(result.current_hc_ratio, 1)}%) "
                        f"overschrijdt de drempel van 15%. Gerichte prioriteits-triaging en "
                        f"proactieve escalatielogica kunnen dit verlagen."
                    ),
                    expected_impact=f"Target: HC-ratio ≤ 15% (huidig: {_fmt_nl(result.current_hc_ratio, 1)}%)",
                    timeline="kort",
                    owner="Team Lead",
                    priority="hoog",
                )
            )

        # Aanbeveling: negatieve cases opvolgen
        if result.negative_cases:
            n = len(result.negative_cases)
            recs.append(
                Recommendation(
                    title=f"Opvolging {n} negatieve tickets",
                    description=(
                        f"Er zijn {n} negatieve tickets (≤ 2★) in {result.current_label}. "
                        f"Zie de deep-dive sectie voor ticket-ID's, ziekenhuizen en volledige comments."
                    ),
                    expected_impact="Directe klantherstelling — potentiële scoreverbetering bij hercontact",
                    timeline="kort",
                    owner="Service Manager",
                    priority="hoog",
                )
            )

        # Aanbeveling: verdwenen ziekenhuizen heractiveren
        if result.hospitals_disappeared:
            n = len(result.hospitals_disappeared)
            recs.append(
                Recommendation(
                    title=f"Heractivering {n} ontbrekend{'e' if n > 1 else ''} ziekenhuis{'en' if n > 1 else ''}",
                    description=(
                        f"De volgende ziekenhuizen zijn niet actief in {result.current_label}: "
                        f"{', '.join(result.hospitals_disappeared)}. "
                        f"Controleer data-aanlevering en neem contact op."
                    ),
                    expected_impact="Volledigheid rapportage en continuïteitsborging",
                    timeline="kort",
                    owner="Service Manager",
                    priority="midden",
                )
            )

        # Aanbeveling: commentaarrate verhogen
        cs = result.current_summary
        if cs and cs.pct_with_comment < 40.0:
            recs.append(
                Recommendation(
                    title="Klantbetrokkenheid verhogen (commentaarrate)",
                    description=(
                        f"Slechts {_fmt_nl(cs.pct_with_comment, 1)}% van de tickets bevat "
                        f"een klantcomment (target: ≥ 40%). Overweeg een e-mailreminder of "
                        f"een kortere feedback-trigger na afhandeling."
                    ),
                    expected_impact="Rijkere kwalitatieve data voor toekomstige analyses",
                    timeline="middellang",
                    owner="Service Manager",
                    priority="midden",
                )
            )

        # Aanbeveling: nieuwe thema's opvolgen
        new_themes = [t for t in result.negative_themes if t.status == "NIEUW"]
        if new_themes:
            theme_names = ", ".join(t.theme_key for t in new_themes)
            recs.append(
                Recommendation(
                    title=f"Nieuw feedbackthema opvolgen: {theme_names}",
                    description=(
                        f"Het thema '{theme_names}' verschijnt voor het eerst in {result.current_label}. "
                        f"Vroege interventie voorkomt dat dit structureel wordt."
                    ),
                    expected_impact="Preventie van structureel negatief thema",
                    timeline="middellang",
                    owner="Team Lead",
                    priority="midden",
                )
            )

        # Sorteer: hoog → midden → laag
        order = {"hoog": 0, "midden": 1, "laag": 2}
        recs.sort(key=lambda r: order.get(r.priority, 3))
        return recs

    # ------------------------------------------------------------------
    # Intern — follow-up acties per tijdshorizon
    # ------------------------------------------------------------------

    def _build_follow_up_actions(self, result: EvolutionResult) -> list[FollowUpAction]:
        """Genereer follow-up acties per tijdshorizon (kort / middellang / lang)."""
        actions: list[FollowUpAction] = []

        # Korte termijn (< 1 maand)
        if result.negative_cases:
            actions.append(
                FollowUpAction(
                    action=f"Contacteer de {len(result.negative_cases)} negatief scorende klanten "
                    f"(zie deep-dive sectie) — herstelgesprek plannen.",
                    horizon="kort",
                    owner="Service Manager",
                )
            )
        if result.hospitals_disappeared:
            actions.append(
                FollowUpAction(
                    action=f"Verifieer data-aanlevering voor: {', '.join(result.hospitals_disappeared)}.",
                    horizon="kort",
                    owner="Service Manager",
                )
            )
        if result.current_hc_ratio > 15.0:
            actions.append(
                FollowUpAction(
                    action="Review prioriteitslogica — reduceer HC-tickets naar ≤ 15%.",
                    horizon="kort",
                    owner="Team Lead",
                )
            )

        # Middellange termijn (1-3 maanden)
        rti = result.response_time_insight
        if rti and rti.avg_days > 10.0:
            actions.append(
                FollowUpAction(
                    action=f"Implementeer responstijdmonitoring — huidig gem. {_fmt_nl(rti.avg_days, 1)} d (target: ≤ 10 d).",
                    horizon="middellang",
                    owner="Service Manager",
                )
            )
        cs = result.current_summary
        if cs and cs.pct_with_comment < 40.0:
            actions.append(
                FollowUpAction(
                    action="Activeer feedback-reminder in ticket-workflow om commentaarrate te verhogen.",
                    horizon="middellang",
                    owner="Team Lead",
                )
            )

        # Lange termijn (3+ maanden)
        actions.append(
            FollowUpAction(
                action=f"Hervalideer KPI-targets op basis van {result.current_label}-realisaties.",
                horizon="lang",
                owner="Service Manager",
            )
        )
        if result.delta_avg_score < 0:
            actions.append(
                FollowUpAction(
                    action=f"Analyseer de oorzaak van de score-daling ({_fmt_nl(result.delta_avg_score, 2)}) "
                    f"en stel een verbeterplan op.",
                    horizon="lang",
                    owner="Team Lead",
                )
            )

        return actions

    # ------------------------------------------------------------------
    # Intern — visuele analyse (beslissing 8)
    # ------------------------------------------------------------------

    def _build_visual_analysis(self, result: EvolutionResult) -> VisualAnalysis:
        """
        Genereer narratieve beschrijvingen per subplot (beslissing 8).

        Gebaseerd op de beschikbare data — geen externe grafiekanalyse nodig.
        """
        scored_months = [dp for dp in result.monthly_timeline if dp.avg_score > 0]

        # Subplot 1 — Scoretrend
        if scored_months:
            best = max(scored_months, key=lambda dp: dp.avg_score)
            worst = min(scored_months, key=lambda dp: dp.avg_score)
            trend_dir = (
                "stijgend"
                if result.delta_avg_score > 0.05
                else ("dalend" if result.delta_avg_score < -0.05 else "stabiel")
            )
            s1 = (
                f"De scoretrend is **{trend_dir}** over de analyseperiode. "
                f"Beste maand: **{best.period}** ({_fmt_nl(best.avg_score, 2)} ★). "
                f"Laagste maand: **{worst.period}** ({_fmt_nl(worst.avg_score, 2)} ★)."
            )
        else:
            s1 = "Geen gescoorde periodes beschikbaar voor trendanalyse."

        # Subplot 2 — Maandvolume
        if result.monthly_timeline:
            total_months = len(result.monthly_timeline)
            max_vol = max(result.monthly_timeline, key=lambda dp: dp.total_tickets)
            s2 = (
                f"Het ticketvolume verdeelt zich over {total_months} periodes. "
                f"Piekmaand: **{max_vol.period}** ({max_vol.total_tickets} tickets)."
            )
        else:
            s2 = "Geen maandvolume beschikbaar."

        # Subplot 3 — Prioriteitscompositie
        if result.current_hc_ratio > 0:
            hc_dir = "hoger" if result.current_hc_ratio > result.baseline_hc_ratio else "lager"
            s3 = (
                f"De HC-ratio (High/Critical) is **{hc_dir}** dan de baseline: "
                f"{_fmt_nl(result.current_hc_ratio, 1)}% vs {_fmt_nl(result.baseline_hc_ratio, 1)}% baseline."
            )
        else:
            s3 = "Geen prioriteitsdata beschikbaar."

        # Subplot 4 — Ziekenhuisbenchmark
        if result.hospital_shortlist:
            best_h = max(
                [h for h in result.hospital_shortlist if h.current_score is not None],
                key=lambda h: h.current_score or 0,
                default=None,
            )
            worst_h = min(
                [h for h in result.hospital_shortlist if h.current_score is not None],
                key=lambda h: h.current_score or 0,
                default=None,
            )
            parts_h = []
            if best_h and best_h.current_score is not None:
                parts_h.append(
                    f"Best presterend: **{best_h.hospital}** ({_fmt_nl(best_h.current_score, 2)} ★)"
                )
            if worst_h and worst_h.current_score is not None and worst_h != best_h:
                parts_h.append(
                    f"aandachtspunt: **{worst_h.hospital}** ({_fmt_nl(worst_h.current_score, 2)} ★)"
                )
            s4 = ". ".join(parts_h) + "." if parts_h else "Zie ziekenhuisvergelijking voor details."
        else:
            s4 = "Zie ziekenhuisvergelijking voor details."

        return VisualAnalysis(
            subplot1_scoretrend=s1,
            subplot2_volume=s2,
            subplot3_priority=s3,
            subplot4_hospitals=s4,
        )

    # ------------------------------------------------------------------
    # Intern — keerpuntanalyse
    # ------------------------------------------------------------------

    def _build_turning_point_analysis(self, result: EvolutionResult) -> str:
        """
        Identificeer keerpunten in de tijdlijn: dieptepunt, doorbraak, topmaanden.
        """
        scored = [dp for dp in result.monthly_timeline if dp.avg_score > 0]
        if len(scored) < 2:
            return ""

        worst = min(scored, key=lambda dp: dp.avg_score)
        best = max(scored, key=lambda dp: dp.avg_score)

        parts: list[str] = []
        parts.append(
            f"**Dieptepunt:** {worst.period} — {_fmt_nl(worst.avg_score, 2)} ★ "
            f"({_fmt_nl(worst.pct_negative, 1)}% negatief)."
        )
        if best.period != worst.period:
            parts.append(f"**Topmaand:** {best.period} — {_fmt_nl(best.avg_score, 2)} ★.")

        # Laatste 3 periodes — richting bepalen
        if len(scored) >= 3:
            last_3 = scored[-3:]
            if all(last_3[i].avg_score <= last_3[i + 1].avg_score for i in range(2)):
                parts.append("De **laatste 3 periodes** tonen een aanhoudende **stijgende trend**.")
            elif all(last_3[i].avg_score >= last_3[i + 1].avg_score for i in range(2)):
                parts.append(
                    "De **laatste 3 periodes** tonen een aanhoudende **dalende trend** — opvolging aanbevolen."
                )

        # Fase-transitie
        fasen = list({dp.fase for dp in result.monthly_timeline})
        if len(fasen) > 1:
            parts.append(
                f"De analyse beslaat {len(fasen)} halfjaarperiodes: {', '.join(sorted(fasen))}."
            )

        return " ".join(parts)

    # ------------------------------------------------------------------
    # Intern — i18n-helper
    # ------------------------------------------------------------------

    def _get_i18n(self, path: str) -> list[str] | str:
        """
        Haal een waarde op uit de i18n-boom via stippelpad.

        Args:
            path: Stippelpad, bv. "insights.score_decline.licht"

        Returns:
            De gevonden waarde (str of list[str]) of een lege string als niet gevonden.
        """
        parts = path.split(".")
        node: dict | str | list = self._t
        for part in parts:
            if isinstance(node, dict):
                node = node.get(part, "")
            else:
                return ""
        return node  # type: ignore[return-value]

    def _pick(self, options: list[str] | str, **kwargs: object) -> str:
        """
        Kies een willekeurige variant en formatteer met kwargs.

        Args:
            options: Eén string of een lijst van alternatieven.
            **kwargs: Formatteervariabelen.

        Returns:
            Geformatteerde string, of lege string bij fout.
        """
        if not options:
            return ""
        text = self._rng.choice(options) if isinstance(options, list) else options
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
