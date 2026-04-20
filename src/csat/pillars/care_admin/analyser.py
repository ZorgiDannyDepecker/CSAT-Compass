"""
ZORGI CARE ADMIN-analyser voor CSAT-Compass.

Erft PillarAnalyser en voegt CARE ADMIN-specifieke drempelwaardecontroles toe.
"""

import pandas as pd
from loguru import logger

from csat.core.analysers.base_analyser import KpiResult
from csat.core.analysers.pillar_analyser import PillarAnalyser

from . import config as care_admin_config


class CareAdminAnalyser(PillarAnalyser):
    """
    Analyser voor de ZORGI CARE ADMIN-pijler.

    Voegt KPI-statusevaluatie toe op basis van CARE ADMIN-drempelwaarden:
    - Reactiegraad ≥ REACTIEGRAAD_MIN (momenteel N/A — ADR-006)
    - High/Critical-ratio ≤ 15%
    - Gemiddelde CSAT-score ≥ AVG_SCORE_MIN (TBD na data-exploratie)
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Args:
            df: Volledig geladen DataFrame (alle pijlers of al gefilterd op CARE ADMIN)
        """
        super().__init__(df, pillar_key="care_admin")

    def analyse(self, period: str) -> KpiResult:
        """
        Analyseer de ZORGI CARE ADMIN-pijler voor de opgegeven periode
        en logt drempelwaarschuwingen automatisch.

        Args:
            period: Periodestring 'YYYY-MM'

        Returns:
            KpiResult met CARE ADMIN KPI's
        """
        result = super().analyse(period)
        self._evaluate_thresholds(result)
        return result

    def _evaluate_thresholds(self, result: KpiResult) -> None:
        """
        Vergelijk KPI's met CARE ADMIN-drempelwaarden en log het resultaat.

        Args:
            result: Ingevuld KpiResult na analyse
        """
        # Reactiegraad — niet evalueerbaar (zie ADR-006)
        if care_admin_config.REACTIEGRAAD_MIN is not None:
            if result.reactiegraad < care_admin_config.REACTIEGRAAD_MIN:
                logger.warning(
                    f"[CareAdminAnalyser] ⚠️ {result.period} — Reactiegraad te laag: "
                    f"{result.reactiegraad}% < {care_admin_config.REACTIEGRAAD_MIN}% (drempel)"
                )
            else:
                logger.info(
                    f"[CareAdminAnalyser] ✅ {result.period} — Reactiegraad OK: "
                    f"{result.reactiegraad}% ≥ {care_admin_config.REACTIEGRAAD_MIN}%"
                )

        # High/Critical-ratio (Blocker + Critical + Major)
        if result.high_critical_ratio > care_admin_config.HIGH_CRITICAL_MAX:
            logger.warning(
                f"[CareAdminAnalyser] ⚠️ {result.period} — High/Critical te hoog: "
                f"{result.high_critical_ratio}% > {care_admin_config.HIGH_CRITICAL_MAX}% (drempel)"
            )
        else:
            logger.info(
                f"[CareAdminAnalyser] ✅ {result.period} — High/Critical OK: "
                f"{result.high_critical_ratio}% ≤ {care_admin_config.HIGH_CRITICAL_MAX}%"
            )

        # Gemiddelde score — enkel evalueren als drempel al vastgesteld is
        if care_admin_config.AVG_SCORE_MIN is not None and result.avg_score > 0:
            if result.avg_score < care_admin_config.AVG_SCORE_MIN:
                logger.warning(
                    f"[CareAdminAnalyser] ⚠️ {result.period} — Gemiddelde score te laag: "
                    f"{result.avg_score} < {care_admin_config.AVG_SCORE_MIN} (drempel)"
                )
            else:
                logger.info(
                    f"[CareAdminAnalyser] ✅ {result.period} — Gemiddelde score OK: "
                    f"{result.avg_score} ≥ {care_admin_config.AVG_SCORE_MIN}"
                )

    def kpi_status(self, result: KpiResult) -> dict[str, bool]:
        """
        Geef een statusoverzicht van alle actieve CARE ADMIN-KPI's als dict.

        Enkel KPI's waarvoor een drempelwaarde is ingesteld worden opgenomen.
        Reactiegraad is momenteel N/A (zie ADR-006).

        Args:
            result: KpiResult na analyse

        Returns:
            Dict met KPI-naam → True als de drempel gehaald is.
        """
        status: dict[str, bool] = {
            "high_critical_ok": result.high_critical_ratio <= care_admin_config.HIGH_CRITICAL_MAX,
        }
        if care_admin_config.REACTIEGRAAD_MIN is not None:
            status["reactiegraad_ok"] = result.reactiegraad >= care_admin_config.REACTIEGRAAD_MIN
        if care_admin_config.AVG_SCORE_MIN is not None:
            status["avg_score_ok"] = result.avg_score >= care_admin_config.AVG_SCORE_MIN

        return status
