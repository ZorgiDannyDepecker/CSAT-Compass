"""
Abstracte basisklasse voor CSAT-analyses.
Definieert gedeelde KPI-berekeningen voor alle pijlers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd
from loguru import logger

from csat.config.pillars import HIGH_CRITICAL_PRIORITIES


@dataclass
class KpiResult:
    """Container voor KPI-resultaten van één analyseperiode."""

    period: str
    pillar: str
    total_tickets: int = 0
    scored_tickets: int = 0
    reactiegraad: float = 0.0  # % tickets met een CSAT-score
    avg_score: float = 0.0  # gemiddelde CSAT-score (alleen gescoorde tickets)
    high_critical_count: int = 0  # absoluut aantal High/Critical-tickets
    high_critical_ratio: float = 0.0  # % High/Critical t.o.v. totaal
    hospitals: list[str] = field(default_factory=list)
    per_hospital: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Geef de KPI-waarden terug als platte dict (zonder per_hospital detail)."""
        return {
            "period": self.period,
            "pillar": self.pillar,
            "total_tickets": self.total_tickets,
            "scored_tickets": self.scored_tickets,
            "reactiegraad": self.reactiegraad,
            "avg_score": self.avg_score,
            "high_critical_count": self.high_critical_count,
            "high_critical_ratio": self.high_critical_ratio,
            "hospitals": len(self.hospitals),
        }


class BaseAnalyser(ABC):
    """
    Abstracte basisanalyser — definieert gedeelde KPI-berekeningen die elke
    pijleranalyser erft en eventueel overschrijft.

    Gedeelde methoden (beschikbaar voor alle subklassen):
    - _calc_reactiegraad()     — % tickets met score
    - _calc_avg_score()        — gemiddelde CSAT-score
    - _calc_high_critical()    — % High/Critical prioriteit
    - _calc_mom_trend()        — Month-over-Month delta
    - _group_by_hospital()     — KPI-aggregatie per ziekenhuis
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Args:
            df: DataFrame afkomstig van een loader, kolomnamen conform V_CSAT_1
        """
        self._df = df.copy()

    # ------------------------------------------------------------------
    # Abstracte methoden — verplicht te implementeren per pijler
    # ------------------------------------------------------------------

    @abstractmethod
    def analyse(self, period: str) -> KpiResult:
        """
        Voer de volledige analyse uit voor de opgegeven periode.

        Args:
            period: Periodestring 'YYYY-MM'

        Returns:
            KpiResult met alle KPI-waarden voor de opgegeven periode
        """
        ...

    # ------------------------------------------------------------------
    # Gedeelde KPI-berekeningen
    # ------------------------------------------------------------------

    def _calc_reactiegraad(self, df: pd.DataFrame) -> tuple[int, int, float]:
        """
        Bereken de reactiegraad: % tickets waarbij een CSAT-score is ingevuld.

        Returns:
            Tuple (totaal_tickets, scored_tickets, reactiegraad_pct)
            Reactiegraad is 0.0 als het DataFrame leeg is.
        """
        total = len(df)
        scored = int(df["score"].notna().sum())
        rate = round((scored / total * 100), 1) if total > 0 else 0.0
        return total, scored, rate

    def _calc_avg_score(self, df: pd.DataFrame) -> float:
        """
        Bereken de gemiddelde CSAT-score, enkel over tickets met een score.

        Returns:
            Gemiddelde score afgerond op 2 decimalen, of 0.0 als er geen scores zijn.
        """
        scored = df[df["score"].notna()]
        if scored.empty:
            return 0.0
        return round(float(scored["score"].mean()), 2)

    def _calc_high_critical(self, df: pd.DataFrame) -> tuple[int, float]:
        """
        Bereken het aantal en percentage High/Critical-prioriteitstickets.

        Returns:
            Tuple (hc_count, hc_ratio_pct)
            hc_ratio is 0.0 als het DataFrame leeg is.
        """
        total = len(df)
        hc_count = int(df["priority"].isin(HIGH_CRITICAL_PRIORITIES).sum())
        hc_ratio = round((hc_count / total * 100), 1) if total > 0 else 0.0
        return hc_count, hc_ratio

    def _calc_mom_trend(
        self,
        current_df: pd.DataFrame,
        previous_df: pd.DataFrame,
        metric: str = "avg_score",
    ) -> float:
        """
        Bereken de Month-over-Month (MoM) delta voor een metriek.

        Args:
            current_df:  DataFrame huidige maand
            previous_df: DataFrame vorige maand
            metric:      'avg_score' of 'reactiegraad'

        Returns:
            Verschil in procentpunten of scorepunten (positief = verbetering).
            Afgerond op 1 decimaal. Geeft 0.0 terug als vorige maand geen data heeft.

        Raises:
            ValueError: Als een onbekende metric wordt opgegeven.
        """
        if previous_df.empty:
            logger.debug("[BaseAnalyser] Vorige maand heeft geen data — MoM trend = 0.0")
            return 0.0

        if metric == "avg_score":
            current_val = self._calc_avg_score(current_df)
            previous_val = self._calc_avg_score(previous_df)
        elif metric == "reactiegraad":
            _, _, current_val = self._calc_reactiegraad(current_df)
            _, _, previous_val = self._calc_reactiegraad(previous_df)
        else:
            raise ValueError(f"Onbekende metric: '{metric}' — kies 'avg_score' of 'reactiegraad'")

        return round(current_val - previous_val, 1)

    def _group_by_hospital(self, df: pd.DataFrame) -> dict[str, dict]:
        """
        Aggregeer KPI's per ziekenhuis.

        Args:
            df: DataFrame (al gefilterd op pijler en periode)

        Returns:
            Dict met ziekenhuisnaam als sleutel en KPI-waarden als dict.
            Lege dict als het DataFrame leeg is.
        """
        if df.empty:
            return {}

        result: dict[str, dict] = {}
        for hospital, group in df.groupby("hospital"):
            total, scored, reactiegraad = self._calc_reactiegraad(group)
            hc_count, hc_ratio = self._calc_high_critical(group)
            avg = self._calc_avg_score(group)
            result[str(hospital)] = {
                "total_tickets": total,
                "scored_tickets": scored,
                "reactiegraad": reactiegraad,
                "avg_score": avg,
                "high_critical_count": hc_count,
                "high_critical_ratio": hc_ratio,
            }
        return result
