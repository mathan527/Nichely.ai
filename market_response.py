from typing import List, Dict, Any
from pydantic import BaseModel

class MarketTrend(BaseModel):
    name: str
    value: float

class Demographics(BaseModel):
    age_group: str
    percentage: float

class Competitor(BaseModel):
    name: str
    market_share: float
    strengths: List[str]
    weaknesses: List[str]
    threat_level: str

class GrowthFactor(BaseModel):
    factor: str
    impact: int  # 1-10 scale
    description: str

class Region(BaseModel):
    name: str
    market_share: float

class GeographicDistribution(BaseModel):
    regions: List[Region]

class Challenge(BaseModel):
    challenge: str
    severity: int  # 1-10 scale
    description: str

class MarketData(BaseModel):
    size: float
    trends: List[MarketTrend]
    demographics: List[Demographics]
    competitors: List[Competitor]
    growth_factors: List[GrowthFactor]

class MarketAnalysis(BaseModel):
    market_data: MarketData
    geographic_distribution: GeographicDistribution
    key_challenges: List[Challenge]

def create_market_response(keyword: str, reddit_data: List[str], market_data: Dict[str, Any]) -> MarketAnalysis:
    """Create a properly structured market analysis response"""
    
    # Extract market size and growth from market data
    size = float(market_data.get("market_size", 0))
    
    # Create trends from market data trends
    trends = [
        MarketTrend(name=k, value=v)
        for k, v in market_data.get("trends", {}).items()
    ]
    
    # Create demographics (mock data for now)
    demographics = [
        Demographics(age_group="18-24", percentage=25),
        Demographics(age_group="25-34", percentage=35),
        Demographics(age_group="35-44", percentage=25),
        Demographics(age_group="45+", percentage=15)
    ]
    
    # Create competitors from market data
    competitors = [
        Competitor(
            name=comp["name"],
            market_share=comp.get("market_share", 0),
            strengths=comp.get("strengths", []),
            weaknesses=comp.get("weaknesses", []),
            threat_level=comp.get("threat_level", "Medium")
        )
        for comp in market_data.get("competitors", [])
    ]
    
    # Create growth factors from market data
    growth_factors = []
    for idx, segment in enumerate(market_data.get("segments", [])):
        growth_factors.append(
            GrowthFactor(
                factor=segment["name"],
                impact=min(10, max(1, int(segment["score"] * 10))),
                description=segment.get("characteristics", ["No description"])[0]
            )
        )
    
    # Create geographic distribution (mock data for now)
    geo_dist = GeographicDistribution(regions=[
        Region(name="North America", market_share=40),
        Region(name="Europe", market_share=30),
        Region(name="Asia", market_share=20),
        Region(name="Rest of World", market_share=10)
    ])
    
    # Create challenges from Reddit data
    challenges = []
    for idx, discussion in enumerate(reddit_data[:5]):
        challenges.append(
            Challenge(
                challenge=f"Challenge {idx + 1}",
                severity=min(10, max(1, (5 - idx))),  # Higher severity for earlier items
                description=discussion[:200]  # Truncate long descriptions
            )
        )
    
    # Create the full market analysis
    analysis = MarketAnalysis(
        market_data=MarketData(
            size=size,
            trends=trends,
            demographics=demographics,
            competitors=competitors,
            growth_factors=growth_factors
        ),
        geographic_distribution=geo_dist,
        key_challenges=challenges
    )
    
    return analysis