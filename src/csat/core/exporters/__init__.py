"""
Exporters voor CSAT-Compass.

Beschikbare exporters:
- ReportExporter: genereert NL/FR markdown-rapporten vanuit KpiResult
"""

from .report_exporter import ReportExporter

__all__ = ["ReportExporter"]
