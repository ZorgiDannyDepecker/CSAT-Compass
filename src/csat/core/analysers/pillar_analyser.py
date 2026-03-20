"""
Pijleranalyser voor CSAT-Compass.

Filtert het DataFrame op pijler (product-kolom) en berekent KPI's
per periode en per ziekenhuis.
"""

import pandas as pd
from loguru import logger

from csat.config.pillars import PILLAR_REGISTRY
from csat.utils.date_utils import filter_period, filter_ytd, previous_period

from .base_analyser import BaseAnalyser, KpiResult


class PillarAnalyser(BaseAnalyser):
    """
    Analyser voor één specifieke ZORGI-pijler.

    Filtert de data op de product-kolom en berekent KPI's
    per opgegeven periode en per ziekenhuis.

    Args:
        df:          Volledig geladen DataFrame (alle pijlers)
        pillar_key:  Pijlersleutel uit PILLAR_REGISTRY (bv. 'pharma', 'care', 'zorgi')
    """

    def __init__(self, df: pd.DataFrame, pillar_key: str) -> None:
        super().__init__(df)

        if pillar_key not in PILLAR_REGISTRY:
            raise ValueError(
                f"Onbekende pijler: '{pillar_key}' — kies uit {sorted(PILLAR_REGISTRY)}"
            )

        self._pillar_key = pillar_key
        self._pillar_config = PILLAR_REGISTRY[pillar_key]
        self._pillar_df = self._filter_pillar(df)

    # ------------------------------------------------------------------
    # Intern — pijlerfilter
    # ------------------------------------------------------------------

    def _filter_pillar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter het DataFrame op de producten van deze pijler.

        De 'zorgi'-pijler bevat geen productfilter en aggregeert alle pijlers.
        """
        products = self._pillar_config.get("products", [])

        if not products:
            # zorgi = aggregatie over alle pijlers, geen filter
            logger.debug(
                f"[PillarAnalyser:{self._pillar_key}] Geen productfilter — volledige dataset"
            )
            return df.copy()

        products_upper = [p.upper() for p in products]
        mask = df["product"].str.strip().str.upper().isin(products_upper)
        filtered = df[mask].copy()

        logger.info(
            f"[PillarAnalyser:{self._pillar_key}] {len(filtered):,} rijen na filter "
            f"op producten: {products}"
        )
        return filtered

    # ------------------------------------------------------------------
    # Publieke analyse-methoden
    # ------------------------------------------------------------------

    def analyse(self, period: str) -> KpiResult:
        """
        Bereken KPI's voor de opgegeven maand.

        Args:
            period: Periodestring 'YYYY-MM'

        Returns:
            KpiResult met reactiegraad, avg_score, High/Critical-ratio
            en per-ziekenhuis detail voor de opgegeven periode.
        """
        current_df = filter_period(self._pillar_df, period)
        prev_period = previous_period(period)
        previous_df = filter_period(self._pillar_df, prev_period)

        total, scored, reactiegraad = self._calc_reactiegraad(current_df)
        avg_score = self._calc_avg_score(current_df)
        hc_count, hc_ratio = self._calc_high_critical(current_df)
        per_hospital = self._group_by_hospital(current_df)

        mom_score = self._calc_mom_trend(current_df, previous_df, metric="avg_score")
        mom_reactiegraad = self._calc_mom_trend(current_df, previous_df, metric="reactiegraad")

        logger.info(
            f"[PillarAnalyser:{self._pillar_key}] {period} — "
            f"{total:,} tickets | reactiegraad {reactiegraad}% (MoM {mom_reactiegraad:+.1f}%) | "
            f"gem. score {avg_score} (MoM {mom_score:+.2f}) | H/C {hc_ratio}%"
        )

        result = KpiResult(
            period=period,
            pillar=self._pillar_key,
            total_tickets=total,
            scored_tickets=scored,
            reactiegraad=reactiegraad,
            avg_score=avg_score,
            high_critical_count=hc_count,
            high_critical_ratio=hc_ratio,
            hospitals=sorted(per_hospital.keys()),
            per_hospital=per_hospital,
        )

        # Sla MoM-trends op als extra attributen (niet in dataclass om uitbreidbaarheid te bewaren)
        result.mom_score = mom_score  # type: ignore[attr-defined]
        result.mom_reactiegraad = mom_reactiegraad  # type: ignore[attr-defined]

        return result

    def analyse_ytd(self, year: int, up_to_month: int) -> KpiResult:
        """
        Bereken geaggregeerde KPI's voor het lopende jaar (YTD).

        Args:
            year:         Het doeljaar
            up_to_month:  Einmaand (inclusief), 1-12

        Returns:
            KpiResult met geaggregeerde KPI's voor het volledige YTD-bereik.
            Geen MoM-trend (niet van toepassing bij YTD).
        """
        ytd_df = filter_ytd(self._pillar_df, year, up_to_month)

        total, scored, reactiegraad = self._calc_reactiegraad(ytd_df)
        avg_score = self._calc_avg_score(ytd_df)
        hc_count, hc_ratio = self._calc_high_critical(ytd_df)
        per_hospital = self._group_by_hospital(ytd_df)

        period_label = f"{year}-YTD-{up_to_month:02d}"

        logger.info(
            f"[PillarAnalyser:{self._pillar_key}] YTD {year} t/m maand {up_to_month} — "
            f"{total:,} tickets | reactiegraad {reactiegraad}% | gem. score {avg_score}"
        )

        return KpiResult(
            period=period_label,
            pillar=self._pillar_key,
            total_tickets=total,
            scored_tickets=scored,
            reactiegraad=reactiegraad,
            avg_score=avg_score,
            high_critical_count=hc_count,
            high_critical_ratio=hc_ratio,
            hospitals=sorted(per_hospital.keys()),
            per_hospital=per_hospital,
        )
