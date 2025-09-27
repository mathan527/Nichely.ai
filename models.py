from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel

class LeaderboardEntry(BaseModel):
    keyword: str
    search_count: int
    market_potential: float | None = None
    success_metrics: dict | None = None
    last_searched: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StartupMetrics(BaseModel):
    market_size: float  # Total addressable market in USD
    growth_potential: float  # YoY growth rate
    innovation_score: float  # Technical innovation rating
    competition_level: float  # Market competition intensity
    user_demand: float  # Current market demand
    profit_margin: float  # Expected profit margin
    acquisition_cost: float  # Customer acquisition cost estimate
    lifetime_value: float  # Customer lifetime value estimate

class RevenueStream(BaseModel):
    name: str
    description: str
    pricing_model: str
    estimated_revenue: str
    target_segment: str

class TechnologyStack(BaseModel):
    core_technologies: List[str]
    infrastructure: List[str]
    third_party_services: List[str]
    development_requirements: Dict[str, str]

class StartupIdea(BaseModel):
    id: str  # Unique identifier for the startup
    name: str  # Startup name
    tagline: str  # Catchy one-liner
    description: str  # Detailed business description
    problem_statement: List[str]  # Key problems being solved
    solution_highlights: List[str]  # How the startup solves these problems
    target_market: Dict[str, Any]  # Market segments and size
    business_model: str  # Business model type (SaaS, marketplace, etc.)
    revenue_streams: List[RevenueStream]  # Multiple revenue streams
    technology_stack: TechnologyStack  # Technical requirements
    metrics: StartupMetrics  # Key business metrics
    competitive_analysis: List[Dict[str, str]]  # Competitor analysis
    go_to_market: Dict[str, str]  # Marketing and launch strategy
    funding_requirements: Dict[str, float]  # Initial investment needs
    financial_projections: Dict[str, float]  # 3-year projections
    team_requirements: List[Dict[str, str]]  # Key roles needed
    risk_analysis: List[Dict[str, str]]  # Potential risks and mitigations
    implementation_roadmap: Dict[str, Dict[str, str]]  # Detailed timeline
    chart_data: Dict[str, str]  # Visualizations

class NicheIdea(BaseModel):
    title: str
    description: str
    pain_points: List[str]
    potential_score: float
    competition_level: str
    monthly_searches: int
    revenue_potential: str
    metrics: StartupMetrics
    innovation_highlights: List[str]
    market_validation: Dict[str, Any]
    competitive_advantages: List[str]
    chart_data: Dict[str, str]
    implementation_timeline: Dict[str, str]

class MarketAnalysisResponse(BaseModel):
    keyword: str
    market_analysis: Dict[str, Any]  # Market analysis data
    sentiment_analysis: Dict[str, Any]  # Sentiment analysis results
    visualizations: Dict[str, str]  # Base64 encoded visualizations
    discussions: List[str]  # Relevant market discussions
    startup_ideas: List[StartupIdea]  # Generated startup opportunities

