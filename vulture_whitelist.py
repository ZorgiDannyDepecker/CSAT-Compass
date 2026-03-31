# vulture_whitelist.py
# =============================================================================
# Vulture — whitelist voor bekende "dode code" die wél in gebruik is
#
# Vulture detecteert code die nergens in Python wordt aangeroepen.
# Sommige code wordt echter gebruikt buiten de Python-scope:
#   - Jinja2-templates (via EvolutionExporter._build_context)
#   - i18n-sleutels (via _get_i18n stippelpad-lookup)
#   - Design system constanten (via externe tools/dashboards)
#   - pytest fixtures (automatisch opgepikt door pytest)
#   - Dataclass-velden (via dataclasses.asdict / template-context)
# =============================================================================

# --- InsightsBundle velden — gebruikt in Jinja2-templates ---
from csat.core.insights.insights_generator import InsightsBundle  # noqa: F401

InsightsBundle.executive_summary
InsightsBundle.critical_findings
InsightsBundle.positive_developments
InsightsBundle.recommendations
InsightsBundle.follow_up_actions
InsightsBundle.visual_analysis
InsightsBundle.turning_point_analysis
InsightsBundle.type_analysis_narrative
InsightsBundle.priority_analysis_narrative
InsightsBundle.response_time_narrative

# --- VisualAnalysis velden — gebruikt in Jinja2-templates ---
from csat.core.insights.insights_generator import VisualAnalysis  # noqa: F401

VisualAnalysis.subplot1_scoretrend
VisualAnalysis.subplot2_volume
VisualAnalysis.subplot3_priority
VisualAnalysis.subplot4_hospitals

# --- CriticalFinding velden — gebruikt in Jinja2-templates ---
from csat.core.insights.insights_generator import CriticalFinding  # noqa: F401

CriticalFinding.title
CriticalFinding.description
CriticalFinding.severity
CriticalFinding.causal_factor

# --- PositiveDevelopment velden — gebruikt in Jinja2-templates ---
from csat.core.insights.insights_generator import PositiveDevelopment  # noqa: F401

PositiveDevelopment.title
PositiveDevelopment.description

# --- Recommendation velden — gebruikt in Jinja2-templates ---
from csat.core.insights.insights_generator import Recommendation  # noqa: F401

Recommendation.title
Recommendation.description
Recommendation.expected_impact
Recommendation.timeline
Recommendation.owner
Recommendation.priority

# --- FollowUpAction velden — gebruikt in Jinja2-templates ---
from csat.core.insights.insights_generator import FollowUpAction  # noqa: F401

FollowUpAction.action
FollowUpAction.horizon
FollowUpAction.owner

# --- ZORGI Design System constanten — gebruikt in visualisaties en dashboards ---
from csat.utils.zorgi_theme import (  # noqa: F401
    ZORGI_BORDEAUX,
    ZORGI_BODY_TEXT,
    ZORGI_FONT_PRIMARY,
    ZORGI_FONT_FALLBACK,
    ZORGI_FONT_STACK,
    ZORGI_GRADIENT_CSS,
    ZORGI_GRADIENT_STOPS,
    ZORGI_LIGHT_PURPLE,
    ZORGI_PILLAR_COLORS,
    ZORGI_WHITE,
)

# --- PILLAR_REGISTRY velden — gebruikt in rapport-exports en dashboards ---
from csat.config.pillars import PILLAR_REGISTRY  # noqa: F401

# --- KpiStatus enum waarden — gebruikt in templates en tests ---
from csat.core.analysers.evolution_result import KpiStatus  # noqa: F401

KpiStatus.OK
KpiStatus.WARNING
KpiStatus.AT_RISK
KpiStatus.UNKNOWN

# --- EvolutionResult velden — gebruikt in Jinja2-templates via exporter context ---
from csat.core.analysers.evolution_result import EvolutionResult  # noqa: F401

EvolutionResult.benchmark_h2
EvolutionResult.hospital_shortlist
EvolutionResult.score_distribution_baseline
EvolutionResult.score_distribution_current

# --- sanitize_comment — publieke API, gebruikt in scripts ---
from csat.core.analysers.evolution_analyser import sanitize_comment  # noqa: F401

# --- get_pillar_for_domain — publieke API, gebruikt in loaders ---
from csat.config.pillars import get_pillar_for_domain  # noqa: F401
