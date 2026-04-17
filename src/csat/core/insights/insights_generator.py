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
- Taalondersteuning NL/FR via _ls(nl, fr) helper

Beslissingen:
- beslissing 1:  Volledig regelgebaseerd — geen LLM
- beslissing 7:  Gedeeld tussen evolutie + maandrapport
- beslissing 8:  Visuele analyse per subplot
- beslissing 9:  Aanbevelingen met impact / tijdlijn / eigenaar
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import UTC

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
    type_analysis_narrative: str = ""
    priority_analysis_narrative: str = ""
    response_time_narrative: str = ""


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
    voor reproduceerbaarheid. Volledige taalondersteuning NL/FR via _ls() helper.

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
            type_analysis_narrative=self._build_type_analysis_narrative(result),
            priority_analysis_narrative=self._build_priority_analysis_narrative(result),
            response_time_narrative=self._build_response_time_narrative(result),
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

    def _ls(self, nl: str, fr: str) -> str:
        """
        Geef de tekst terug in de huidige rapportagetaal.

        Args:
            nl: Nederlandstalige tekst
            fr: Franstalige tekst

        Returns:
            nl als self._lang == 'nl', anders fr
        """
        return fr if self._lang == "fr" else nl

    @property
    def _day_unit(self) -> str:
        """Dagafkorting: 'd' (NL) of 'j' (FR)."""
        return "j" if self._lang == "fr" else "d"

    def _translate_theme_key(self, key: str) -> str:
        """Vertaal een thema-sleutel via i18n (bv. 'automatisering' → 'Automatisation')."""
        value: object = self._t.get("evolution", {}).get("theme", {}).get(key, key)
        return str(value)

    def _translate_trend_breadth(self, breadth: str) -> str:
        """Vertaal trend_breadth waarde naar de huidige taal."""
        _nl = {"breed": "breed", "beperkt": "beperkt", "gemengd": "gemengd"}
        _fr = {"breed": "large", "beperkt": "limité", "gemengd": "mixte"}
        return (_fr if self._lang == "fr" else _nl).get(breadth, breadth)

    # ------------------------------------------------------------------
    # Intern — executive summary
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

        # 2. Scoreverdeling-narratief — taalafhankelijk opgebouwd
        sd = result.score_distribution_current
        if sd and sd.counts:
            n = sum(sd.counts.values())
            if n > 0:
                top_level = max(range(1, 6), key=lambda k: sd.counts.get(k, 0))
                top_pct = sd.percentages.get(top_level, 0.0)
                if top_level == 5:
                    narrative = self._ls(
                        f"Van de {n} antwoorden scoort {_fmt_nl(top_pct, 1)}% een volle 5★.",
                        f"Sur {n} réponses, {_fmt_nl(top_pct, 1)}% donnent la note maximale de 5★.",
                    )
                elif top_level >= 4:
                    narrative = self._ls(
                        f"Van de {n} antwoorden beoordeelt {_fmt_nl(top_pct, 1)}% het ticket positief ({top_level}★ of hoger).",
                        f"Sur {n} réponses, {_fmt_nl(top_pct, 1)}% évaluent le ticket positivement ({top_level}★ ou plus).",
                    )
                else:
                    narrative = self._ls(
                        f"Van de {n} antwoorden is de meerderheid ({_fmt_nl(top_pct, 1)}%) geconcentreerd rond {top_level}★.",
                        f"Sur {n} réponses, la majorité ({_fmt_nl(top_pct, 1)}%) se concentre autour de {top_level}★.",
                    )
                parts.append(narrative)

        # 3. Contextuele nuancering: kleine daling maar positief % stabiel
        if delta < 0 and abs(delta) < 0.15 and result.current_pct_positive > 75.0:
            nuance = self._pick(
                self._get_i18n("insights.nuance.stable_positive"),
                pct=_fmt_nl(result.current_pct_positive, 1),
            )
            if nuance and parts:
                connector = self._pick(self._get_i18n("insights.connectors.contrast"))
                parts[-1] = f"{parts[-1]} {connector} {nuance[0].lower()}{nuance[1:]}"

        # 4. Responstijd-correlatie
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

        # 5. KPI-achievement narrative
        if result.kpi_targets:
            n_on_track = sum(1 for kt in result.kpi_targets if kt.on_track)
            n_total = len(result.kpi_targets)
            if n_on_track == n_total:
                parts.append(
                    self._ls(
                        f"Alle {n_total} KPI-targets zijn na de meetperiode al bereikt of overtroffen.",
                        f"Les {n_total} objectifs KPI ont déjà été atteints ou dépassés après la période de mesure.",
                    )
                )
            elif n_on_track >= n_total * 0.7:
                parts.append(
                    self._ls(
                        f"{n_on_track} van de {n_total} KPI-targets zijn op schema.",
                        f"{n_on_track} des {n_total} objectifs KPI sont en bonne voie.",
                    )
                )

        # 6. Slotboodschap
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

        return "\n".join(f"- {p}" for p in parts if p)

    # ------------------------------------------------------------------
    # Intern — kritieke bevindingen
    # ------------------------------------------------------------------

    def _build_critical_findings(  # noqa: C901
        self, result: EvolutionResult
    ) -> list[CriticalFinding]:
        """
        Genereer 3-5 kritieke bevindingen met causaliteit en ernst.

        Elke bevinding bevat titel, beschrijving, ernst en causale factor.
        """
        findings: list[CriticalFinding] = []

        # Bevinding 1: Score-evolutie
        delta = result.delta_avg_score
        if abs(delta) >= 0.1:
            sev = self.classify_severity(abs(delta), "score_delta")
            emoji = "✅" if delta > 0 else ("🔴" if sev == "significant" else "⚠️")
            trend_word = self._ls(
                "gestegen" if delta > 0 else "gedaald",
                "en hausse" if delta > 0 else "en baisse",
            )
            findings.append(
                CriticalFinding(
                    title=self._ls(
                        f"{emoji} Scoretrend: {trend_word} met {_fmt_nl(abs(delta), 2)}",
                        f"{emoji} Tendance des scores : {trend_word} de {_fmt_nl(abs(delta), 2)}",
                    ),
                    description=self._ls(
                        (
                            f"De gemiddelde CSAT-score is {trend_word} van "
                            f"{_fmt_nl(result.baseline_avg_score, 2)} naar "
                            f"{_fmt_nl(result.current_avg_score, 2)} "
                            f"({result.baseline_label} → {result.current_label}).  \n"
                            f"De breedte van deze beweging is {self._translate_trend_breadth(result.trend_breadth)}."
                        ),
                        (
                            f"Le score CSAT moyen a {'progressé' if delta > 0 else 'reculé'} de "
                            f"{_fmt_nl(result.baseline_avg_score, 2)} à "
                            f"{_fmt_nl(result.current_avg_score, 2)} "
                            f"({result.baseline_label} → {result.current_label}).  \n"
                            f"L'étendue de ce mouvement est {self._translate_trend_breadth(result.trend_breadth)}."
                        ),
                    ),
                    severity="hoog" if sev == "significant" else sev,
                    causal_factor=self._ls(
                        "Score-evolutie over de analyseperiode",
                        "Évolution du score sur la période analysée",
                    ),
                )
            )

        # Bevinding 2: Responstijd-correlatie
        rti = result.response_time_insight
        if rti and rti.correlation_score is not None and abs(rti.correlation_score) > 0.05:
            r = rti.correlation_score
            du = self._day_unit
            if r > 0.1:
                desc = self._ls(
                    (
                        f"Er is een positieve correlatie (r={_fmt_nl(r, 3)}) tussen "
                        f"responstijd en klanttevredenheid.  \nPositieve scores: "
                        f"gem. {_fmt_nl(rti.avg_positive_days or 0, 1)} {du} | "
                        f"Negatieve scores: gem. {_fmt_nl(rti.avg_negative_days or 0, 1)} {du}."
                    )
                    if rti.avg_positive_days is not None and rti.avg_negative_days is not None
                    else (
                        f"Er is een positieve correlatie (r={_fmt_nl(r, 3)}) tussen "
                        f"responstijd en klanttevredenheid: snellere afhandeling gaat samen met hogere scores."
                    ),
                    (
                        f"Il existe une corrélation positive (r={_fmt_nl(r, 3)}) entre le délai de réponse "
                        f"et la satisfaction.  \nScores positifs : moy. {_fmt_nl(rti.avg_positive_days or 0, 1)} {du} | "
                        f"Scores négatifs : moy. {_fmt_nl(rti.avg_negative_days or 0, 1)} {du}."
                    )
                    if rti.avg_positive_days is not None and rti.avg_negative_days is not None
                    else (
                        f"Il existe une corrélation positive (r={_fmt_nl(r, 3)}) entre le délai de réponse "
                        f"et la satisfaction : traiter plus vite conduit à de meilleures notes."
                    ),
                )
                findings.append(
                    CriticalFinding(
                        title=self._ls(
                            f"⏱️ Responstijd correleert met klanttevredenheid (r={_fmt_nl(r, 3)})",
                            f"⏱️ Corrélation délai-satisfaction (r={_fmt_nl(r, 3)})",
                        ),
                        description=desc,
                        severity="hoog",
                        causal_factor=self._ls(
                            "Responstijd is aantoonbaar gelinkt aan CSAT-score",
                            "Le délai de réponse est clairement lié au score CSAT",
                        ),
                    )
                )
            elif r < -0.1:
                findings.append(
                    CriticalFinding(
                        title=self._ls(
                            f"⏱️ Negatieve correlatie responstijd ↔ score (r={_fmt_nl(r, 3)})",
                            f"⏱️ Corrélation négative délai ↔ score (r={_fmt_nl(r, 3)})",
                        ),
                        description=self._ls(
                            (
                                f"Langere responstijden gaan samen met hogere scores (r={_fmt_nl(r, 3)}).  \n"
                                f"Mogelijke verklaring: complexere tickets vragen meer tijd maar worden positiever beoordeeld."
                            ),
                            (
                                f"Des délais plus longs s'accompagnent de meilleures notes (r={_fmt_nl(r, 3)}).  \n"
                                f"Explication possible : les tickets complexes demandent plus de temps mais sont mieux évalués."
                            ),
                        ),
                        severity="medium",
                        causal_factor=self._ls(
                            "Complexe tickets correleren met hogere scores",
                            "Les tickets complexes sont corrélés à de meilleures notes",
                        ),
                    )
                )

        # Bevinding: correlatie-omslag (baseline vs huidig)
        if rti and rti.correlation_score is not None and rti.baseline_correlation_score is not None:
            b_corr = rti.baseline_correlation_score
            c_corr = rti.correlation_score
            if b_corr < -0.05 and c_corr > 0.05:
                findings.append(
                    CriticalFinding(
                        title=self._ls(
                            "🔄 Omslag in correlatie: responstijd niet meer de hoofdoorzaak",
                            "🔄 Inversion de corrélation : le délai n'est plus la cause principale",
                        ),
                        description=self._ls(
                            (
                                f"In de baseline was er een negatieve correlatie "
                                f"(r={_fmt_nl(b_corr, 3)}) tussen responstijd en score: "
                                f"lange wachttijden veroorzaakten ontevredenheid.  \n"
                                f"In {result.current_label} is die correlatie omgeslagen naar "
                                f"positief (r={_fmt_nl(c_corr, 3)}): snelle maar onvolledige "
                                f"afhandelingen vormen nu de belangrijkste oorzaak van negatieve scores.  \n"
                                f"Dit is een fundamenteel andere en beter beheersbare uitdaging."
                            ),
                            (
                                f"Dans la baseline, la corrélation était négative "
                                f"(r={_fmt_nl(b_corr, 3)}) : les longs délais causaient l'insatisfaction.  \n"
                                f"Dans {result.current_label}, cette corrélation est devenue positive "
                                f"(r={_fmt_nl(c_corr, 3)}) : des clôtures rapides mais incomplètes "
                                f"constituent désormais la principale cause de scores négatifs.  \n"
                                f"C'est un défi fondamentalement différent et mieux maîtrisable."
                            ),
                        ),
                        severity="hoog",
                        causal_factor=self._ls(
                            "Dynamiekwissel: van wachttijd-gedreven naar kwaliteitsgedreven ontevredenheid",
                            "Changement de dynamique : de l'attente à la qualité de traitement",
                        ),
                    )
                )
            elif b_corr > 0.05 and c_corr < -0.05:
                findings.append(
                    CriticalFinding(
                        title=self._ls(
                            "⚠️ Omslag in correlatie: responstijd opnieuw een risicofactor",
                            "⚠️ Inversion de corrélation : le délai redevient un facteur de risque",
                        ),
                        description=self._ls(
                            (
                                f"De correlatie responstijd↔score sloeg om van "
                                f"positief (r={_fmt_nl(b_corr, 3)}, baseline) naar "
                                f"negatief (r={_fmt_nl(c_corr, 3)}, {result.current_label}).  \n"
                                f"Langere wachttijden beginnen opnieuw samen te gaan met lagere scores.  \n"
                                f"Opvolging van responstijd-SLA's is aanbevolen."
                            ),
                            (
                                f"La corrélation délai↔score s'est inversée de "
                                f"positive (r={_fmt_nl(b_corr, 3)}, baseline) à "
                                f"négative (r={_fmt_nl(c_corr, 3)}, {result.current_label}).  \n"
                                f"Des délais plus longs recommencent à s'accompagner de notes plus basses.  \n"
                                f"Un suivi des SLA de délai de réponse est recommandé."
                            ),
                        ),
                        severity="hoog",
                        causal_factor=self._ls(
                            "Responstijd opnieuw gelinkt aan ontevredenheid",
                            "Le délai de réponse lié à nouveau à l'insatisfaction",
                        ),
                    )
                )

        # Bevinding 3: Negatief % boven drempel
        if result.current_pct_negative > 10.0:
            sev = "hoog" if result.current_pct_negative > 15.0 else "medium"
            findings.append(
                CriticalFinding(
                    title=self._ls(
                        f"🔴 Negatief percentage: {_fmt_nl(result.current_pct_negative, 1)}%",
                        f"🔴 Taux négatif : {_fmt_nl(result.current_pct_negative, 1)}%",
                    ),
                    description=self._ls(
                        (
                            f"{_fmt_nl(result.current_pct_negative, 1)}% van de gescoorde tickets "
                            f"is negatief (≤ 2★) in {result.current_label}.  \n"
                            f"Baseline was {_fmt_nl(result.baseline_pct_negative, 1)}%.  \n"
                            f"Zie de diepgaande analyse van de negatieve feedback voor details."
                        ),
                        (
                            f"{_fmt_nl(result.current_pct_negative, 1)}% des tickets évalués "
                            f"sont négatifs (≤ 2★) dans {result.current_label}.  \n"
                            f"Baseline : {_fmt_nl(result.baseline_pct_negative, 1)}%.  \n"
                            f"Voir l'analyse approfondie du feedback négatif."
                        ),
                    ),
                    severity=sev,
                    causal_factor=self._ls(
                        "Hoog aandeel ontevreden klanten",
                        "Taux élevé de clients insatisfaits",
                    ),
                )
            )

        # Bevinding 4: HC-ratio boven drempel
        if result.current_hc_ratio > 15.0:
            findings.append(
                CriticalFinding(
                    title=self._ls(
                        f"🔴 HC-ratio: {_fmt_nl(result.current_hc_ratio, 1)}%",
                        f"🔴 Taux H/C : {_fmt_nl(result.current_hc_ratio, 1)}%",
                    ),
                    description=self._ls(
                        (
                            f"De High/Critical-ratio bedraagt {_fmt_nl(result.current_hc_ratio, 1)}% "
                            f"in {result.current_label} (drempel: 15%).  \n"
                            f"Baseline: {_fmt_nl(result.baseline_hc_ratio, 1)}%."
                        ),
                        (
                            f"Le taux High/Critical s'élève à {_fmt_nl(result.current_hc_ratio, 1)}% "
                            f"dans {result.current_label} (seuil : 15%).  \n"
                            f"Baseline : {_fmt_nl(result.baseline_hc_ratio, 1)}%."
                        ),
                    ),
                    severity="hoog" if result.current_hc_ratio > 25.0 else "medium",
                    causal_factor=self._ls(
                        "Verhoogd aandeel urgente tickets",
                        "Part élevée de tickets urgents",
                    ),
                )
            )

        # Bevinding 5: Ziekenhuisretentie onder drempel
        if result.hospital_retention_pct < 75.0 and result.hospitals_disappeared:
            n = len(result.hospitals_disappeared)
            findings.append(
                CriticalFinding(
                    title=self._ls(
                        f"🏥 Ziekenhuisretentie: {_fmt_nl(result.hospital_retention_pct, 1)}%",
                        f"🏥 Rétention hôpitaux : {_fmt_nl(result.hospital_retention_pct, 1)}%",
                    ),
                    description=self._ls(
                        (
                            f"{n} {'ziekenhuis' if n == 1 else 'ziekenhuizen'} uit de baseline "
                            f"{'is' if n == 1 else 'zijn'} niet aanwezig in {result.current_label}.  \n"
                            f"Controleer of dit data-aanlevering of stopzetting betreft.  \n"
                            f"→ *Zie § 8 — Verdwenen ziekenhuizen voor het volledig overzicht.*"
                        ),
                        (
                            f"{n} {'hôpitaux' if n > 1 else 'hôpital'} de la baseline "
                            f"{'est absent' if n == 1 else 'sont absents'} dans {result.current_label}.  \n"
                            f"Vérifiez si cela est dû à la transmission des données ou à un arrêt.  \n"
                            f"→ *Voir § 8 — Hôpitaux absents pour la liste complète.*"
                        ),
                    ),
                    severity="hoog" if result.hospital_retention_pct < 50.0 else "medium",
                    causal_factor=self._ls(
                        "Verminderde dekking of data-probleem",
                        "Couverture réduite ou problème de données",
                    ),
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
        du = self._day_unit

        if result.delta_avg_score >= 0.1:
            devs.append(
                PositiveDevelopment(
                    title=self._ls(
                        "Scoreverbetering t.o.v. baseline",
                        "Amélioration du score vs baseline",
                    ),
                    description=self._ls(
                        f"De gemiddelde CSAT-score steeg van {_fmt_nl(result.baseline_avg_score, 2)} naar {_fmt_nl(result.current_avg_score, 2)} (+{_fmt_nl(result.delta_avg_score, 2)}).",
                        f"Le score CSAT moyen a progressé de {_fmt_nl(result.baseline_avg_score, 2)} à {_fmt_nl(result.current_avg_score, 2)} (+{_fmt_nl(result.delta_avg_score, 2)}).",
                    ),
                )
            )

        delta_pos = result.current_pct_positive - result.baseline_pct_positive
        if delta_pos >= 2.0:
            devs.append(
                PositiveDevelopment(
                    title=self._ls(
                        "Stijging % positieve scores",
                        "Hausse du % de scores positifs",
                    ),
                    description=self._ls(
                        f"Het aandeel positieve beoordelingen (≥ 4★) nam toe van {_fmt_nl(result.baseline_pct_positive, 1)}% naar {_fmt_nl(result.current_pct_positive, 1)}% (+{_fmt_nl(delta_pos, 1)}pp).",
                        f"La part d'évaluations positives (≥ 4★) a augmenté de {_fmt_nl(result.baseline_pct_positive, 1)}% à {_fmt_nl(result.current_pct_positive, 1)}% (+{_fmt_nl(delta_pos, 1)}pp).",
                    ),
                )
            )

        delta_resp = result.current_avg_response_days - result.baseline_avg_response_days
        if delta_resp < -1.0:
            devs.append(
                PositiveDevelopment(
                    title=self._ls(
                        "Kortere gemiddelde responstijd",
                        "Réduction du délai de réponse moyen",
                    ),
                    description=self._ls(
                        f"De gemiddelde responstijd daalde van {_fmt_nl(result.baseline_avg_response_days, 1)} naar {_fmt_nl(result.current_avg_response_days, 1)} dagen ({_fmt_nl(delta_resp, 1)} {du}).",
                        f"Le délai de réponse moyen a diminué de {_fmt_nl(result.baseline_avg_response_days, 1)} à {_fmt_nl(result.current_avg_response_days, 1)} jours ({_fmt_nl(delta_resp, 1)} {du}).",
                    ),
                )
            )

        resolved = [t for t in result.negative_themes if t.status == "OPGELOST"]
        if resolved:
            theme_names = ", ".join(self._translate_theme_key(t.theme_key) for t in resolved)
            devs.append(
                PositiveDevelopment(
                    title=self._ls(
                        f"Opgeloste feedbackthema's ({len(resolved)})",
                        f"Thèmes de feedback résolus ({len(resolved)})",
                    ),
                    description=self._ls(
                        f"De volgende thema's waren aanwezig in de baseline maar zijn verdwenen in {result.current_label}: {theme_names}.",
                        f"Les thèmes suivants étaient présents dans la baseline mais ont disparu dans {result.current_label} : {theme_names}.",
                    ),
                )
            )

        delta_hc = result.current_hc_ratio - result.baseline_hc_ratio
        if delta_hc < -2.0:
            devs.append(
                PositiveDevelopment(
                    title=self._ls(
                        "Daling High/Critical-ratio",
                        "Baisse du taux High/Critical",
                    ),
                    description=self._ls(
                        f"De HC-ratio daalde van {_fmt_nl(result.baseline_hc_ratio, 1)}% naar {_fmt_nl(result.current_hc_ratio, 1)}% ({_fmt_nl(delta_hc, 1)}pp).",
                        f"Le taux H/C a diminué de {_fmt_nl(result.baseline_hc_ratio, 1)}% à {_fmt_nl(result.current_hc_ratio, 1)}% ({_fmt_nl(delta_hc, 1)}pp).",
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
        du = self._day_unit

        rti = result.response_time_insight
        if rti and rti.correlation_score is not None and rti.correlation_score > 0.1:
            recs.append(
                Recommendation(
                    title=self._ls(
                        "Responstijd optimaliseren",
                        "Optimiser le délai de réponse",
                    ),
                    description=self._ls(
                        f"De positieve correlatie (r={_fmt_nl(rti.correlation_score, 3)}) toont aan dat kortere responstijden direct bijdragen aan hogere CSAT-scores.  \nHuidig gemiddelde: {_fmt_nl(result.current_avg_response_days, 1)} {du}.",
                        f"La corrélation positive (r={_fmt_nl(rti.correlation_score, 3)}) montre que des délais plus courts contribuent directement à de meilleures notes CSAT.  \nDélai actuel : {_fmt_nl(result.current_avg_response_days, 1)} {du}.",
                    ),
                    expected_impact=self._ls(
                        "Verwachte scoreverbetering +0,10 tot +0,20 bij halvering responstijd",
                        "Amélioration attendue +0,10 à +0,20 en réduisant le délai de moitié",
                    ),
                    timeline="kort",
                    owner="Service Manager",
                    priority="hoog",
                )
            )

        if result.current_hc_ratio > 15.0:
            recs.append(
                Recommendation(
                    title=self._ls(
                        "HC-ratio terugdringen",
                        "Réduire le taux High/Critical",
                    ),
                    description=self._ls(
                        f"De High/Critical-ratio ({_fmt_nl(result.current_hc_ratio, 1)}%) overschrijdt de drempel van 15%.  \nGerichte prioriteits-triaging en proactieve escalatielogica kunnen dit verlagen.",
                        f"Le taux High/Critical ({_fmt_nl(result.current_hc_ratio, 1)}%) dépasse le seuil de 15%.  \nUn triage ciblé des priorités et une logique d'escalade proactive peuvent le réduire.",
                    ),
                    expected_impact=self._ls(
                        f"Target: HC-ratio ≤ 15% (huidig: {_fmt_nl(result.current_hc_ratio, 1)}%)",
                        f"Objectif : taux H/C ≤ 15% (actuel : {_fmt_nl(result.current_hc_ratio, 1)}%)",
                    ),
                    timeline="kort",
                    owner="Team Lead",
                    priority="hoog",
                )
            )

        if result.negative_cases:
            n = len(result.negative_cases)
            recs.append(
                Recommendation(
                    title=self._ls(
                        f"Opvolging {n} negatieve tickets",
                        f"Suivi des {n} tickets négatifs",
                    ),
                    description=self._ls(
                        f"Er zijn {n} negatieve tickets (≤ 2★) in {result.current_label}.  \nZie de diepgaande analyse voor ticket-ID's, ziekenhuizen en volledige comments.",
                        f"Il y a {n} tickets négatifs (≤ 2★) dans {result.current_label}.  \nVoir la section analyse approfondie pour les ID, hôpitaux et commentaires complets.",
                    ),
                    expected_impact=self._ls(
                        "Directe klantherstelling — potentiële scoreverbetering bij hercontact",
                        "Rétablissement direct de la relation client — amélioration potentielle du score",
                    ),
                    timeline="kort",
                    owner="Service Manager",
                    priority="hoog",
                )
            )

        if result.hospitals_disappeared:
            n = len(result.hospitals_disappeared)
            recs.append(
                Recommendation(
                    title=self._ls(
                        f"Heractivering {n} ontbrekend{'e' if n > 1 else ''} {'ziekenhuis' if n == 1 else 'ziekenhuizen'}",
                        f"Réactivation de {n} {'hôpitaux' if n > 1 else 'hôpital'} manquant{'s' if n > 1 else ''}",
                    ),
                    description=self._ls(
                        f"De volgende ziekenhuizen zijn niet actief in {result.current_label} ({len(result.hospitals_disappeared)} ziekenhuizen).  \nControleer data-aanlevering en neem contact op.  \n→ *Zie § 8 — Verdwenen ziekenhuizen voor het volledig overzicht.*",
                        f"Les hôpitaux suivants sont absents dans {result.current_label} ({len(result.hospitals_disappeared)} hôpitaux).  \nVérifiez la transmission des données et prenez contact.  \n→ *Voir § 8 — Hôpitaux absents pour la liste complète.*",
                    ),
                    expected_impact=self._ls(
                        "Volledigheid rapportage en continuïteitsborging",
                        "Complétude du rapport et garantie de continuité",
                    ),
                    timeline="kort",
                    owner="Service Manager",
                    priority="midden",
                )
            )

        cs = result.current_summary
        if cs and cs.pct_with_comment < 40.0:
            recs.append(
                Recommendation(
                    title=self._ls(
                        "Klantbetrokkenheid verhogen (commentaarrate)",
                        "Améliorer l'engagement client (taux de commentaires)",
                    ),
                    description=self._ls(
                        f"Slechts {_fmt_nl(cs.pct_with_comment, 1)}% van de tickets bevat een klantcomment (target: ≥ 40%).  \nOverweeg een e-mailreminder of een kortere feedback-trigger na afhandeling.",
                        f"Seulement {_fmt_nl(cs.pct_with_comment, 1)}% des tickets contiennent un commentaire client (objectif : ≥ 40%).  \nEnvisagez un rappel e-mail ou un déclencheur de feedback plus court après traitement.",
                    ),
                    expected_impact=self._ls(
                        "Rijkere kwalitatieve data voor toekomstige analyses",
                        "Données qualitatives plus riches pour les analyses futures",
                    ),
                    timeline="middellang",
                    owner="Service Manager",
                    priority="midden",
                )
            )

        new_themes = [t for t in result.negative_themes if t.status == "NIEUW"]
        if new_themes:
            theme_names = ", ".join(self._translate_theme_key(t.theme_key) for t in new_themes)
            recs.append(
                Recommendation(
                    title=self._ls(
                        f"Nieuw feedbackthema opvolgen: {theme_names}",
                        f"Suivi du nouveau thème de feedback : {theme_names}",
                    ),
                    description=self._ls(
                        f"Het thema '{theme_names}' verschijnt voor het eerst in {result.current_label}.  \nVroege interventie voorkomt dat dit structureel wordt.",
                        f"Le thème '{theme_names}' apparaît pour la première fois dans {result.current_label}.  \nUne intervention précoce évitera qu'il ne devienne structurel.",
                    ),
                    expected_impact=self._ls(
                        "Preventie van structureel negatief thema",
                        "Prévention d'un thème négatif structurel",
                    ),
                    timeline="middellang",
                    owner="Team Lead",
                    priority="midden",
                )
            )

        order = {"hoog": 0, "midden": 1, "laag": 2}
        recs.sort(key=lambda r: order.get(r.priority, 3))
        return recs

    # ------------------------------------------------------------------
    # Intern — follow-up acties per tijdshorizon
    # ------------------------------------------------------------------

    def _build_follow_up_actions(self, result: EvolutionResult) -> list[FollowUpAction]:
        """Genereer follow-up acties per tijdshorizon (kort / middellang / lang)."""
        actions: list[FollowUpAction] = []
        du = self._day_unit

        if result.negative_cases:
            actions.append(
                FollowUpAction(
                    action=self._ls(
                        f"Contacteer de {len(result.negative_cases)} negatief scorende klanten (zie diepgaande analyse) — herstelgesprek plannen.",
                        f"Contacter les {len(result.negative_cases)} clients ayant donné une note négative (voir section analyse approfondie) — planifier un entretien de rétablissement.",
                    ),
                    horizon="kort",
                    owner="Service Manager",
                )
            )
        if result.hospitals_disappeared:
            actions.append(
                FollowUpAction(
                    action=self._ls(
                        f"Verifieer data-aanlevering voor {len(result.hospitals_disappeared)} ontbrekende ziekenhuizen — zie § 8.",
                        f"Vérifier la transmission des données pour {len(result.hospitals_disappeared)} hôpitaux manquants — voir § 8.",
                    ),
                    horizon="kort",
                    owner="Service Manager",
                )
            )
        if result.current_hc_ratio > 15.0:
            actions.append(
                FollowUpAction(
                    action=self._ls(
                        "Review prioriteitslogica — reduceer HC-tickets naar ≤ 15%.",
                        "Revoir la logique de priorité — réduire les tickets H/C à ≤ 15%.",
                    ),
                    horizon="kort",
                    owner="Team Lead",
                )
            )

        rti = result.response_time_insight
        if rti and rti.avg_days > 10.0:
            actions.append(
                FollowUpAction(
                    action=self._ls(
                        f"Implementeer responstijdmonitoring — huidig gem. {_fmt_nl(rti.avg_days, 1)} {du} (target: ≤ 10 {du}).",
                        f"Mettre en place un suivi des délais — délai actuel {_fmt_nl(rti.avg_days, 1)} {du} (objectif : ≤ 10 {du}).",
                    ),
                    horizon="middellang",
                    owner="Service Manager",
                )
            )
        cs = result.current_summary
        if cs and cs.pct_with_comment < 40.0:
            actions.append(
                FollowUpAction(
                    action=self._ls(
                        "Activeer feedback-reminder in ticket-workflow om commentaarrate te verhogen.",
                        "Activer un rappel de feedback dans le workflow tickets pour augmenter le taux de commentaires.",
                    ),
                    horizon="middellang",
                    owner="Team Lead",
                )
            )

        actions.append(
            FollowUpAction(
                action=self._ls(
                    f"Hervalideer KPI-targets op basis van {result.current_label}-realisaties.",
                    f"Revalider les objectifs KPI sur la base des réalisations {result.current_label}.",
                ),
                horizon="lang",
                owner="Service Manager",
            )
        )
        if result.delta_avg_score < 0:
            actions.append(
                FollowUpAction(
                    action=self._ls(
                        f"Analyseer de oorzaak van de score-daling ({_fmt_nl(result.delta_avg_score, 2)}) en stel een verbeterplan op.",
                        f"Analyser la cause de la baisse du score ({_fmt_nl(result.delta_avg_score, 2)}) et établir un plan d'amélioration.",
                    ),
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
        """
        scored_months = [dp for dp in result.monthly_timeline if dp.avg_score > 0]

        if scored_months:
            best = max(scored_months, key=lambda dp: dp.avg_score)
            worst = min(scored_months, key=lambda dp: dp.avg_score)
            if result.delta_avg_score > 0.05:
                trend_dir = self._ls("stijgend", "à la hausse")
            elif result.delta_avg_score < -0.05:
                trend_dir = self._ls("dalend", "à la baisse")
            else:
                trend_dir = self._ls("stabiel", "stable")
            s1 = self._ls(
                f"De scoretrend is **{trend_dir}** over de analyseperiode.  \nBeste maand: **{best.period}** ({_fmt_nl(best.avg_score, 2)} ★).  \nLaagste maand: **{worst.period}** ({_fmt_nl(worst.avg_score, 2)} ★).",
                f"La tendance des scores est **{trend_dir}** sur la période analysée.  \nMeilleur mois : **{best.period}** ({_fmt_nl(best.avg_score, 2)} ★).  \nMois le plus bas : **{worst.period}** ({_fmt_nl(worst.avg_score, 2)} ★).",
            )
        else:
            s1 = self._ls(
                "Geen gescoorde periodes beschikbaar voor trendanalyse.",
                "Aucune période évaluée disponible pour l'analyse de tendance.",
            )

        if result.monthly_timeline:
            total_months = len(result.monthly_timeline)
            max_vol = max(result.monthly_timeline, key=lambda dp: dp.total_tickets)
            s2 = self._ls(
                f"Het ticketvolume verdeelt zich over {total_months} periodes.  \nPiekmaand: **{max_vol.period}** ({max_vol.total_tickets} tickets).",
                f"Le volume de tickets se répartit sur {total_months} périodes.  \nMois de pointe : **{max_vol.period}** ({max_vol.total_tickets} tickets).",
            )
        else:
            s2 = self._ls("Geen maandvolume beschikbaar.", "Aucun volume mensuel disponible.")

        if result.current_hc_ratio > 0:
            hc_dir = self._ls(
                "hoger" if result.current_hc_ratio > result.baseline_hc_ratio else "lager",
                "plus élevé" if result.current_hc_ratio > result.baseline_hc_ratio else "plus bas",
            )
            s3 = self._ls(
                f"De HC-ratio (High/Critical) is **{hc_dir}** dan de baseline: {_fmt_nl(result.current_hc_ratio, 1)}% vs {_fmt_nl(result.baseline_hc_ratio, 1)}% baseline.",
                f"Le taux H/C est **{hc_dir}** que la baseline : {_fmt_nl(result.current_hc_ratio, 1)}% vs {_fmt_nl(result.baseline_hc_ratio, 1)}% baseline.",
            )
        else:
            s3 = self._ls(
                "Geen prioriteitsdata beschikbaar.", "Aucune donnée de priorité disponible."
            )

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
                    self._ls(
                        f"Best presterend: **{best_h.hospital}** ({_fmt_nl(best_h.current_score, 2)} ★)",
                        f"Meilleure performance : **{best_h.hospital}** ({_fmt_nl(best_h.current_score, 2)} ★)",
                    )
                )
            if worst_h and worst_h.current_score is not None and worst_h != best_h:
                parts_h.append(
                    self._ls(
                        f"Aandachtspunt: **{worst_h.hospital}** ({_fmt_nl(worst_h.current_score, 2)} ★)",
                        f"Point d'attention : **{worst_h.hospital}** ({_fmt_nl(worst_h.current_score, 2)} ★)",
                    )
                )
            s4 = (
                ".  \n".join(parts_h) + "."
                if parts_h
                else self._ls(
                    "Zie ziekenhuisvergelijking voor details.",
                    "Voir la comparaison par hôpital pour les détails.",
                )
            )
        else:
            s4 = self._ls(
                "Zie ziekenhuisvergelijking voor details.",
                "Voir la comparaison par hôpital pour les détails.",
            )

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
            self._ls(
                f"**Dieptepunt:** {worst.period} — {_fmt_nl(worst.avg_score, 2)} ★ ({_fmt_nl(worst.pct_negative, 1)}% negatief).",
                f"**Point bas :** {worst.period} — {_fmt_nl(worst.avg_score, 2)} ★ ({_fmt_nl(worst.pct_negative, 1)}% négatif).",
            )
        )
        if best.period != worst.period:
            parts.append(
                self._ls(
                    f"**Topmaand:** {best.period} — {_fmt_nl(best.avg_score, 2)} ★.",
                    f"**Meilleur mois :** {best.period} — {_fmt_nl(best.avg_score, 2)} ★.",
                )
            )

        if len(scored) >= 3:
            last_3 = scored[-3:]
            if all(last_3[i].avg_score <= last_3[i + 1].avg_score for i in range(2)):
                parts.append(
                    self._ls(
                        "De **laatste 3 periodes** tonen een aanhoudende **stijgende trend**.",
                        "Les **3 dernières périodes** affichent une **tendance à la hausse** soutenue.",
                    )
                )
            elif all(last_3[i].avg_score >= last_3[i + 1].avg_score for i in range(2)):
                parts.append(
                    self._ls(
                        "De **laatste 3 periodes** tonen een aanhoudende **dalende trend** — opvolging aanbevolen.",
                        "Les **3 dernières périodes** affichent une **tendance à la baisse** soutenue — suivi recommandé.",
                    )
                )

        fasen = list({dp.fase for dp in result.monthly_timeline})
        if len(fasen) > 1:
            parts.append(
                self._ls(
                    f"De analyse beslaat {len(fasen)} halfjaarperiodes: {', '.join(sorted(fasen))}.",
                    f"L'analyse couvre {len(fasen)} semestres : {', '.join(sorted(fasen))}.",
                )
            )

        return "  \n".join(parts)

    # ------------------------------------------------------------------
    # Intern — type-analyse narratief
    # ------------------------------------------------------------------

    def _build_type_analysis_narrative(self, result: EvolutionResult) -> str:
        """Genereer narratieve duiding onder de tabel 'Analyse per type'."""
        items = [t for t in result.by_issue_type if t.current_score > 0]
        if not items:
            return ""

        best = max(items, key=lambda t: t.current_score)
        worst = min(items, key=lambda t: t.current_score)
        most_neg_baseline = max(
            [t for t in result.by_issue_type if t.baseline_score > 0],
            key=lambda t: t.baseline_pct_neg,
            default=None,
        )

        parts: list[str] = []

        parts.append(
            self._ls(
                f"**{best.issue_type}** scoort het best in {result.current_label} ({_fmt_nl(best.current_score, 2)} ★): de scope is duidelijker afgebakend en succesvolle afhandeling is beter communiceerbaar naar de klant.",
                f"**{best.issue_type}** obtient les meilleures notes dans {result.current_label} ({_fmt_nl(best.current_score, 2)} ★) : la portée est mieux délimitée et la résolution réussie est plus facilement communiquée au client.",
            )
        )

        if most_neg_baseline and most_neg_baseline.issue_type != best.issue_type:
            parts.append(
                self._ls(
                    f"**{most_neg_baseline.issue_type}** kende in de baseline het hoogste aandeel negatieve scores ({_fmt_nl(most_neg_baseline.baseline_pct_neg, 1)}%) en vertegenwoordigt daarmee het grootste verbeterpotentieel.",
                    f"**{most_neg_baseline.issue_type}** avait le taux de scores négatifs le plus élevé dans la baseline ({_fmt_nl(most_neg_baseline.baseline_pct_neg, 1)}%) et représente donc le plus grand potentiel d'amélioration.",
                )
            )

        if worst.issue_type != best.issue_type:
            parts.append(
                self._ls(
                    f"**{worst.issue_type}** scoort momenteel het laagst ({_fmt_nl(worst.current_score, 2)} ★) — verhoogde opvolging aanbevolen.",
                    f"**{worst.issue_type}** obtient actuellement les notes les plus basses ({_fmt_nl(worst.current_score, 2)} ★) — un suivi renforcé est recommandé.",
                )
            )

        return "\n\n> 💡 ".join(parts)

    # ------------------------------------------------------------------
    # Intern — prioriteit-analyse narratief
    # ------------------------------------------------------------------

    def _build_priority_analysis_narrative(self, result: EvolutionResult) -> str:
        """Genereer narratieve duiding onder de tabel 'Analyse per prioriteit'."""
        items = [p for p in result.by_priority if p.current_score > 0]
        if not items:
            return ""

        worst = min(items, key=lambda p: p.current_score)

        improvable = [p for p in result.by_priority if p.baseline_score > 0 and p.current_score > 0]
        most_improved = (
            max(improvable, key=lambda p: p.current_score - p.baseline_score)
            if improvable
            else None
        )

        high_urgency = [p for p in items if p.priority in ("Blocker", "Critical")]
        low_urgency = [p for p in items if p.priority in ("Trivial", "Minor")]

        parts: list[str] = []

        if worst.priority in ("Trivial", "Minor"):
            parts.append(
                self._ls(
                    f"**{worst.priority}**-tickets scoren het laagst ({_fmt_nl(worst.current_score, 2)} ★). Dit is contra-intuïtief maar verklaarbaar: lage prioriteit in het systeem leidt tot minder aandacht in afhandeling, terwijl de klant het ticket voor zichzelf als relevant beschouwt.",
                    f"Les tickets **{worst.priority}** obtiennent les notes les plus basses ({_fmt_nl(worst.current_score, 2)} ★). C'est contre-intuitif mais explicable : une faible priorité dans le système entraîne moins d'attention dans le traitement, alors que le client considère le ticket comme pertinent.",
                )
            )
        else:
            parts.append(
                self._ls(
                    f"**{worst.priority}**-tickets scoren het laagst ({_fmt_nl(worst.current_score, 2)} ★) — opvolging aanbevolen.",
                    f"Les tickets **{worst.priority}** obtiennent les notes les plus basses ({_fmt_nl(worst.current_score, 2)} ★) — suivi recommandé.",
                )
            )

        if high_urgency:
            avg_high = sum(p.current_score for p in high_urgency) / len(high_urgency)
            avg_low = (
                sum(p.current_score for p in low_urgency) / len(low_urgency)
                if low_urgency
                else None
            )
            if avg_low and avg_high >= avg_low:
                parts.append(
                    self._ls(
                        f"**{' en '.join(p.priority for p in high_urgency)}** scoren hoog (gem. {_fmt_nl(avg_high, 2)} ★): de escalatieprocedure voor urgente problemen werkt.",
                        f"Les tickets **{' et '.join(p.priority for p in high_urgency)}** obtiennent de bonnes notes (moy. {_fmt_nl(avg_high, 2)} ★) : la procédure d'escalade pour les problèmes urgents est efficace.",
                    )
                )

        if most_improved:
            delta = most_improved.current_score - most_improved.baseline_score
            parts.append(
                self._ls(
                    f"**{most_improved.priority}** toont de sterkste verbetering (+{_fmt_nl(delta, 2)} ★ t.o.v. baseline).",
                    f"**{most_improved.priority}** affiche la plus forte progression (+{_fmt_nl(delta, 2)} ★ par rapport à la baseline).",
                )
            )

        return "\n\n> 💡 ".join(parts)

    # ------------------------------------------------------------------
    # Intern — responstijd narratief
    # ------------------------------------------------------------------

    def _build_response_time_narrative(self, result: EvolutionResult) -> str:
        """Genereer narratieve duiding onder de tabel 'Responstijd per score-niveau'."""
        rows = [r for r in result.response_time_by_score.values() if r.current_days is not None]
        if not rows:
            return ""

        shortest = min(rows, key=lambda r: r.current_days or 0.0)
        longest = max(rows, key=lambda r: r.current_days or 0.0)
        short_days = shortest.current_days or 0.0
        long_days = longest.current_days or 0.0

        rti = result.response_time_insight
        du = self._day_unit
        parts: list[str] = []

        if shortest.score_level <= 2:
            stars_short = "★" * shortest.score_level
            parts.append(
                self._ls(
                    f"**Opvallend paradox:** tickets met de laagste scores ({stars_short}) hebben de kortste responstijd ({_fmt_nl(short_days, 1)} {du}).  \nDit wijst op snelle maar onvolledige afhandeling: het ticket wordt snel gesloten zonder dat het onderliggende probleem structureel is opgelost.",
                    f"**Paradoxe notable :** les tickets avec les notes les plus basses ({stars_short}) ont le délai de réponse le plus court ({_fmt_nl(short_days, 1)} {du}).  \nCela indique une clôture rapide mais incomplète : le ticket est fermé rapidement sans que le problème sous-jacent soit résolu de manière structurelle.",
                )
            )

        if longest.score_level >= 4:
            stars_long = "★" * longest.score_level + "☆" * (5 - longest.score_level)
            parts.append(
                self._ls(
                    f"Tickets met score {stars_long} hebben de langste gemiddelde responstijd ({_fmt_nl(long_days, 1)} {du}).  \nDit zijn vaak complexere dossiers die meer aandacht vragen, maar waarvan de grondige afhandeling positief gewaardeerd wordt.",
                    f"Les tickets avec score {stars_long} ont le délai de réponse moyen le plus long ({_fmt_nl(long_days, 1)} {du}).  \nCe sont souvent des dossiers complexes qui demandent plus d'attention, mais dont le traitement approfondi est apprécié positivement.",
                )
            )

        if rti and rti.correlation_score is not None:
            r = rti.correlation_score
            if r > 0.1:
                parts.append(
                    self._ls(
                        f"De positieve correlatie (r={_fmt_nl(r, 3)}) bevestigt dat kwaliteit van afhandeling primair is — niet enkel de snelheid.",
                        f"La corrélation positive (r={_fmt_nl(r, 3)}) confirme que la qualité du traitement est primordiale — pas seulement la rapidité.",
                    )
                )
            elif r < -0.1:
                parts.append(
                    self._ls(
                        f"De negatieve correlatie (r={_fmt_nl(r, 3)}) bevestigt dat kortere responstijden samengaan met hogere klanttevredenheid.",
                        f"La corrélation négative (r={_fmt_nl(r, 3)}) confirme que des délais plus courts s'accompagnent d'une meilleure satisfaction client.",
                    )
                )

        return "\n\n> 💡 ".join(parts)

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

    def _generate_issue_type_insight(self, df_comparison) -> str:  # type: ignore[override]
        """Genereert de inzichttekst voor de issue type insight-box.

        Gebruikt de bestaande _ls(nl, fr) helper voor taalwisseling.
        Retourneert altijd str, nooit None.
        """
        import math

        # Fallback bij lege data
        valid = df_comparison.dropna(subset=["score_curr"])
        if valid.empty:
            return self._ls(
                "Geen issue type data beschikbaar voor deze periode.",
                "Aucune donnée de type de ticket disponible pour cette période.",
            )

        # Laagst scorend type
        lowest_row = valid.loc[valid["score_curr"].idxmin()]
        lowest_type = lowest_row["issue_type"]
        lowest_score = lowest_row["score_curr"]
        lowest_neg = lowest_row["pct_neg_curr"]

        # Grootste verbetering
        valid_delta = valid.dropna(subset=["delta_score"])
        best_delta_type = (
            valid_delta.loc[valid_delta["delta_score"].idxmax(), "issue_type"]
            if not valid_delta.empty
            else None
        )
        best_delta = valid_delta["delta_score"].max() if not valid_delta.empty else float("nan")

        # Typespecifieke aanbevelingen
        aanbevelingen = {
            "Incident": self._ls(
                "Verplicht slotbericht + root cause veld als prioritaire actie.",
                "Message de clôture obligatoire + champ cause racine comme action prioritaire.",
            ),
            "Request for Configuration": self._ls(
                "Configuratieproces reviewen op doorlooptijd.",
                "Réviser le processus de configuration sur le délai de traitement.",
            ),
            "Request for Improvement": self._ls(
                "Verbeterverzoeken actief opvolgen en terugkoppelen.",
                "Assurer un suivi actif et un retour sur les demandes d'amélioration.",
            ),
            "Request for Information": self._ls(
                "Kennisbank uitbreiden om herhaalde vragen te reduceren.",
                "Élargir la base de connaissances pour réduire les questions répétées.",
            ),
        }
        aanbeveling = aanbevelingen.get(
            lowest_type,
            self._ls(
                "Opvolging en kwaliteitsreview aanbevolen.",
                "Suivi et révision qualité recommandés.",
            ),
        )

        neg_hoog = not math.isnan(lowest_neg) and lowest_neg > 10.0
        same_type = best_delta_type == lowest_type

        if same_type and neg_hoog:
            return self._ls(
                f"{lowest_type}: Sterkste verbetering (+{best_delta:.2f}★) maar laagst scorend "
                f"({lowest_score:.2f}★) en {lowest_neg:.1f}% negatief. {aanbeveling}",
                f"{lowest_type} : Amélioration la plus forte (+{best_delta:.2f}★) mais score le plus bas "
                f"({lowest_score:.2f}★) et {lowest_neg:.1f}% négatif. {aanbeveling}",
            )
        if same_type:
            return self._ls(
                f"{lowest_type}: Sterkste verbetering (+{best_delta:.2f}★) en laagst scorend "
                f"({lowest_score:.2f}★). Verdere opvolging aanbevolen.",
                f"{lowest_type} : Amélioration la plus forte (+{best_delta:.2f}★) et score le plus bas "
                f"({lowest_score:.2f}★). Suivi recommandé.",
            )
        if neg_hoog:
            return self._ls(
                f"{lowest_type} blijft laagst scorend ({lowest_score:.2f}★) "
                f"met {lowest_neg:.1f}% negatief. {aanbeveling}",
                f"{lowest_type} reste le score le plus bas ({lowest_score:.2f}★) "
                f"avec {lowest_neg:.1f}% négatif. {aanbeveling}",
            )
        return self._ls(
            f"{lowest_type} blijft laagst scorend ({lowest_score:.2f}★). Verdere monitoring aanbevolen.",
            f"{lowest_type} reste le score le plus bas ({lowest_score:.2f}★). Monitoring recommandé.",
        )

    def _generate_priority_insight(self, df_comparison) -> str:
        """Genereert de inzichttekst voor de prioriteit insight-box.

        Identificeert de prioriteit met de combinatie van
        laagste score_curr EN hoogste pct_neg_curr.
        Retourneert altijd str, nooit None.
        """
        import math
        from datetime import datetime

        # Fallback bij lege data
        valid = df_comparison.dropna(subset=["score_curr", "pct_neg_curr"])
        if valid.empty:
            return self._ls(
                "Geen prioriteitsdata beschikbaar voor deze periode.",
                "Aucune donnée de priorité disponible pour cette période.",
            )

        # Probleem-prioriteit: prioriteit met laagste score_curr
        probleem_row = valid.loc[valid["score_curr"].idxmin()]
        prio = probleem_row["priority"]
        score = probleem_row["score_curr"]
        neg = probleem_row["pct_neg_curr"]

        # Periode-string
        now = datetime.now(tz=UTC).date()
        kwartaal = (now.month - 1) // 3 + 1
        periode_nl = f"Q{kwartaal} {now.year}"
        periode_fr = f"T{kwartaal} {now.year}"

        neg_hoog = not math.isnan(neg) and neg > 10.0

        if neg_hoog:
            return self._ls(
                f"{prio}-tickets: laagste score ({score:.2f}★) én hoogste negatief% "
                f"({neg:.1f}%) in {periode_nl}. Lage prioriteit in het systeem → "
                f"minder aandacht → klant gefrustreerd. Steekproef kwaliteitsreview vereist.",
                f"Tickets {prio} : score le plus bas ({score:.2f}★) et pourcentage négatif "
                f"le plus élevé ({neg:.1f}%) en {periode_fr}. Faible priorité dans le "
                f"système → moins d'attention → client frustré. "
                f"Revue qualité par échantillon requise.",
            )
        return self._ls(
            f"{prio}-tickets scoren het laagst ({score:.2f}★) in {periode_nl}. "
            f"Verdere monitoring aanbevolen.",
            f"Les tickets {prio} ont le score le plus bas ({score:.2f}★) en {periode_fr}. "
            f"Monitoring supplémentaire recommandé.",
        )

    def _generate_feedback_themes(self, df) -> list[dict]:
        """Detecteert negatieve feedbackthema's via keyword matching op het comment-veld.

        Analyseert enkel negatieve tickets (score <= 2).
        Retourneert een lijst van dicts met 'naam' en 'beschrijving'.
        Lege lijst als geen thema's gevonden of geen negatieve tickets.
        """
        import re

        from csat.core.analysers.evolution_analyser import THEME_ACTION_HINTS, THEME_KEYWORDS

        # Themanamen per taal
        _theme_labels_nl = {
            "responstijd": "Responstijd",
            "onvolledig": "Onvolledige oplossing",
            "communicatie": "Communicatie",
            "urgentie": "Urgentieherkenning",
            "automatisering": "Automatisering",
        }
        _theme_labels_fr = {
            "responstijd": "Temps de réponse",
            "onvolledig": "Solution incomplète",
            "communicatie": "Communication",
            "urgentie": "Reconnaissance de l'urgence",
            "automatisering": "Automatisation",
        }

        # Negatieve tickets filteren
        if df is None or df.empty or "score" not in df.columns:
            return []
        neg = df[df["score"].notna() & (df["score"] <= 2)]
        if neg.empty or "comment" not in df.columns:
            return []

        n = len(neg)
        results = []
        for theme_key, keywords in THEME_KEYWORDS.items():
            pattern = "|".join(re.escape(kw) for kw in keywords)
            hits = neg["comment"].fillna("").str.lower().str.contains(pattern, regex=True)
            pct = round(hits.sum() / n * 100, 1)
            if pct > 0:
                labels_nl = _theme_labels_nl
                labels_fr = _theme_labels_fr
                naam = self._ls(
                    labels_nl.get(theme_key, theme_key),
                    labels_fr.get(theme_key, theme_key),
                )
                actie = THEME_ACTION_HINTS.get(theme_key, "")
                beschrijving = self._ls(
                    f"{pct:.0f}% van negatieve tickets — {actie}",
                    f"{pct:.0f}% des tickets négatifs — {actie}",
                )
                results.append({"naam": naam, "beschrijving": beschrijving, "pct": pct})

        # Sorteer op percentage (hoogste eerst), max 4 thema's
        results.sort(key=lambda x: x["pct"], reverse=True)
        return results[:4]
