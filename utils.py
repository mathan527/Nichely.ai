from typing import Dict, List
import logging
from enhanced_visualizations import (
    generate_enhanced_opportunity_chart,
    generate_financial_projections_chart,
    generate_competitor_chart
)

logger = logging.getLogger(__name__)

def enrich_startup_data(startup: Dict) -> Dict:
    """Ensure startup data has all required fields with defaults"""
    base = {
        "name": "",
        "tagline": "",
        "description": "",
        "problem_statement": [],
        "solution_highlights": [],
        "metrics": {
            "market_size": 0,
            "growth_potential": 0,
            "innovation_score": 0,
            "competition_level": 0
        },
        "target_market": {
            "size": 0,
            "segments": [],
            "geography": "Global",
            "growth_rate": "0% YoY"
        },
        "financial_projections": {
            "year1": 0,
            "year2": 0,
            "year3": 0
        },
        "technology_stack": {
            "core_technologies": [],
            "infrastructure": []
        }
    }
    return deep_merge(base, startup)

def generate_startup_charts(startup: Dict) -> Dict:
    """Generate all charts for startup detail page"""
    return {
        "market_analysis": generate_enhanced_opportunity_chart({
            "market_size": startup["metrics"]["market_size"],
            "growth_potential": startup["metrics"]["growth_potential"],
            "innovation_score": startup["metrics"]["innovation_score"],
            "competition_level": startup["metrics"]["competition_level"]
        }),
        "revenue_projection": generate_financial_projections_chart(startup["financial_projections"]),
        "competitor_analysis": generate_competitor_chart(startup.get("competitor_mentions", []))
    }

def deep_merge(base: Dict, update: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = base.copy()
    for key, value in update.items():
        if isinstance(value, dict) and key in result:
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

async def get_cached_startups() -> List[Dict]:
    """Get cached startup data from database or memory"""
    # TODO: Implement proper caching
    return []