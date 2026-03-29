"""
Gedeelde InsightsGenerator voor CSAT-Compass.
Regelgebaseerde interpretatie-engine die EvolutionResult omzet naar narratieve
inzichten: executive summary, kritieke bevindingen, aanbevelingen, follow-up en
visuele analyse.
Gebruik:
    from csat.core.insights import InsightsGenerator, InsightsBundle
"""

from csat.core.insights.insights_generator import InsightsBundle, InsightsGenerator

__all__ = ["InsightsBundle", "InsightsGenerator"]
