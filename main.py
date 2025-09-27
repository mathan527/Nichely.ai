# Nichely - AI Niche Discovery Platform
#! /usr/bin/env python

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from supabase import create_client
from typing import List, Dict, Any
from datetime import datetime
from textblob import TextBlob
import random
import httpx
from contextlib import asynccontextmanager
from analysis import process_niche_analysis

from models import (
    NicheIdea, StartupIdea, StartupMetrics, RevenueStream, 
    TechnologyStack, LeaderboardEntry, MarketAnalysisResponse
)
from visualizations import (
    generate_reddit_visualizations, 
    analyze_reddit_sentiment
)
from enhanced_visualizations import (
    generate_trend_chart,
    generate_competitor_chart,
    generate_feature_impact_chart,
    generate_enhanced_opportunity_chart,
    generate_financial_projections_chart
)
from config import settings
from data_fetchers import fetch_reddit_data

def slugify(text: str) -> str:
    """Convert text to URL-safe slug"""
    import re
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")

def extract_unique_pain_points(discussions: List[str], keyword: str) -> List[Dict[str, Any]]:
    """Extract unique pain points from discussions with their context and sentiment"""
    def create_default_point(message: str) -> Dict[str, Any]:
        """Create a default pain point structure"""
        return {
            "point": message,
            "context": "No detailed context available",
            "sentiment": 0.0,
            "frequency": 1,
            "impact_score": 0.0
        }

    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not isinstance(text, str):
            return ""
        return " ".join(text.lower().split())

    def safe_sentiment_analysis(text: str) -> float:
        """Safely get sentiment score"""
        # Simplified sentiment analysis - not critical for localStorage approach
        try:
            # Basic sentiment based on keywords
            positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome', 'perfect']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'sucks', 'disappointing']
            
            text_lower = text.lower()
            positive_score = sum(1 for word in positive_words if word in text_lower)
            negative_score = sum(1 for word in negative_words if word in text_lower)
            
            if positive_score + negative_score == 0:
                return 0.0
            return (positive_score - negative_score) / (positive_score + negative_score)
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return 0.0

    try:
        # Validate input
        if not isinstance(discussions, list) or not discussions:
            return [create_default_point(f"Insufficient data to analyze {keyword}")]

        keyword = clean_text(keyword)
        if not keyword:
            return [create_default_point("Invalid keyword provided")]

        # Initialize storage
        pain_points_dict = {}
        
        # Pain point indicators
        indicators = {
            "need", "problem", "issue", "difficult", "challenge", 
            "hate", "missing", "lack", "better", "expensive", 
            "inefficient", "hard", "slow", "broken", "unreliable"
        }

        # Process each discussion
        for discussion in discussions:
            if not isinstance(discussion, str) or not discussion.strip():
                continue

            # Clean the discussion text
            clean_discussion = clean_text(discussion)
            if not clean_discussion:
                continue

            # Split into sentences and analyze each
            for sentence in clean_discussion.split(". "):
                if not sentence:
                    continue

                # Check if sentence contains indicator and keyword
                if (any(ind in sentence for ind in indicators) and 
                    keyword in sentence):
                    
                    # Get sentiment and impact
                    sentiment = safe_sentiment_analysis(sentence)
                    word_count = len(sentence.split())
                    impact = abs(sentiment) * word_count

                    # Create unique key for deduplication
                    key = hash(sentence)

                    if key not in pain_points_dict:
                        pain_points_dict[key] = {
                            "point": sentence.capitalize(),
                            "context": clean_discussion[:200],
                            "sentiment": sentiment,
                            "frequency": 1,
                            "impact_score": impact
                        }
                    else:
                        point = pain_points_dict[key]
                        point["frequency"] += 1
                        point["impact_score"] += impact

        # Convert to list and sort by impact
        pain_points = list(pain_points_dict.values())
        
        # Return results with fallback
        if pain_points:
            # Sort by impact score and frequency
            return sorted(
                pain_points,
                key=lambda x: (x["impact_score"] * x["frequency"]),
                reverse=True
            )
        else:
            return [create_default_point(
                f"No specific pain points identified in {keyword} market"
            )]

    except Exception as e:
        print(f"Error in pain points extraction: {str(e)}")
        return [create_default_point(
            f"Error analyzing pain points for {keyword}"
        )]
    
    # Sort by impact score and frequency
    return sorted(
        pain_points,
        key=lambda x: (x["impact_score"] * x["frequency"]),
        reverse=True
    )

def validate_pain_point(pain_point: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean a pain point dictionary"""
    try:
        return {
            "point": str(pain_point.get("point", "Market opportunity identified")),
            "context": str(pain_point.get("context", "No context available"))[:500],
            "sentiment": float(pain_point.get("sentiment", 0.0)),
            "frequency": max(int(pain_point.get("frequency", 1)), 1),
            "impact_score": max(float(pain_point.get("impact_score", 1.0)), 0.1)
        }
    except Exception as e:
        print(f"Error validating pain point: {str(e)}")
        return {
            "point": "Market opportunity identified",
            "context": "No context available",
            "sentiment": 0.0,
            "frequency": 1,
            "impact_score": 1.0
        }

def generate_startup_ideas(discussions: List[str], word_freq: Dict[str, int], keyword: str) -> List[StartupIdea]:
    """Generate a small set of safe startup ideas from pain points.

    This implementation is intentionally simple and defensive: it uses
    the existing pain-point extractor, validates entries, and always
    returns a list of StartupIdea objects (at least one). That removes
    the previous large, duplicated, and syntactically broken implementation.
    """
    startup_ideas: List[StartupIdea] = []

    # Get validated pain points (validate_pain_point is defined above)
    raw_points = extract_unique_pain_points(discussions, keyword)
    pain_points = [validate_pain_point(p) for p in raw_points]

    # Ensure we always have at least one pain point
    if not pain_points:
        pain_points = [validate_pain_point({"point": f"Opportunity in {keyword}"})]

    # Simple business models to generate variations
    business_models = [
        ("saas", "Software as a Service"),
        ("marketplace", "Two-sided Marketplace"),
        ("platform", "Platform Business")
    ]

    # Simple technology stack and revenue stream templates
    default_tech_stack = TechnologyStack(
        core_technologies=["Python", "React", "PostgreSQL"],
        infrastructure=["AWS", "Docker"],
        third_party_services=["Stripe for payments", "SendGrid for emails"],
        development_requirements={
            "Frontend": "2-3 developers",
            "Backend": "2-3 developers",
            "DevOps": "1 developer",
            "Timeline": "4-6 months to MVP"
        }
    )

    for i, (model_key, model_desc) in enumerate(business_models):
        try:
            pp = pain_points[i % len(pain_points)]

            # Build a conservative metrics object
            freq = max(int(pp.get("frequency", 1)), 1)
            impact = max(float(pp.get("impact_score", 1.0)), 0.1)
            sentiment = float(pp.get("sentiment", 0.0))

            metrics = StartupMetrics(
                market_size=min(freq * impact * 5.0, 100.0),
                growth_potential=max(20.0 + sentiment * 20.0, 0.0),
                innovation_score=min(impact * 8.0, 100.0),
                competition_level= min(50.0, 100.0),
                user_demand=min(freq * 10.0, 100.0),
                profit_margin=50.0,
                acquisition_cost=500.0,
                lifetime_value=2500.0
            )

            revenue_streams = [
                RevenueStream(
                    name="Core Service",
                    description=f"Primary {model_desc} offering",
                    pricing_model="Monthly Subscription" if model_key == "saas" else "Transaction Fee",
                    estimated_revenue="$10K - $50K/month",
                    target_segment="SMB"
                )
            ]

            idea_id = slugify(f"{keyword}-{model_key}-{i+1}")
            idea_name = f"{keyword.title()}{model_key.title()}{i+1}"

            startup = StartupIdea(
                id=idea_id,
                name=idea_name,
                tagline=f"{model_desc} for {keyword}",
                description=f"{model_desc} addressing: {pp.get('point')}",
                problem_statement=[pp.get('point', 'General market opportunity')],
                solution_highlights=[f"AI-powered {keyword} optimization", "Automation", "Analytics"],
                target_market={
                    "size": int(metrics.market_size * 10000),
                    "segments": ["SMB"],
                    "geography": "Global",
                    "growth_rate": f"{metrics.growth_potential:.1f}% YoY"
                },
                business_model=model_desc,
                revenue_streams=revenue_streams,
                technology_stack=default_tech_stack,
                metrics=metrics,
                competitive_analysis=[{"name": "Competitor 1", "strength": "Established brand", "weakness": "Legacy tech"}],
                go_to_market={"strategy": "Digital marketing", "channels": "Social media, Content marketing"},
                financial_projections={
                    "year1": float(metrics.market_size * 10000),
                    "year2": float(metrics.market_size * 20000),
                    "year3": float(metrics.market_size * 40000)
                },
                funding_requirements={
                    "seed_round": float(metrics.market_size * 5000),
                    "runway": 12.0
                },
                team_requirements=[{"role": "CTO", "skills": "Full-stack development", "priority": "High"}],
                risk_analysis=[{"risk": "Market competition", "impact": "Medium", "mitigation": "Focus on differentiation"}],
                implementation_roadmap={"Q1": {"milestone": "MVP development", "status": "Planned"}},
                chart_data={"growth_chart": "base64_placeholder", "market_chart": "base64_placeholder"}
            )

            startup_ideas.append(startup)
        except Exception as e:
            # Keep generating others even if one fails
            print(f"generate_startup_ideas: skipped model {model_key} due to: {e}")
            continue

    # Ensure at least one startup idea is returned
    if not startup_ideas:
        startup_ideas.append(
            StartupIdea(
                id=slugify(f"{keyword}-default-1"),
                name=f"{keyword.title()}Idea1",
                tagline=f"Startup idea for {keyword}",
                description=f"Default generated idea for {keyword}",
                problem_statement=[f"Opportunity in {keyword}"],
                solution_highlights=["AI", "Automation"],
                target_market={"size": 100000, "segments": ["SMB"], "geography": "Global", "growth_rate": "10% YoY"},
                business_model="Platform Business",
                revenue_streams=[],
                technology_stack=default_tech_stack,
                metrics=StartupMetrics(market_size=50.0, growth_potential=20.0, innovation_score=40.0, competition_level=50.0, user_demand=50.0, profit_margin=50.0, acquisition_cost=500.0, lifetime_value=2500.0),
                competitive_analysis=[{"name": "Default Competitor", "strength": "Market presence", "weakness": "Innovation gap"}],
                go_to_market={"strategy": "Digital first", "channels": "Online marketing"},
                financial_projections={"year1": 100000.0, "year2": 200000.0, "year3": 400000.0},
                funding_requirements={"seed_round": 100000.0, "runway": 12.0},
                team_requirements=[{"role": "CEO", "skills": "Leadership", "priority": "High"}],
                risk_analysis=[{"risk": "Competition", "impact": "Medium", "mitigation": "Differentiation"}],
                implementation_roadmap={"Phase1": {"milestone": "Launch", "status": "Planned"}},
                chart_data={"market": "placeholder"}
            )
        )

    return startup_ideas

# Initialize FastAPI app
app = FastAPI(title="Nichely - AI Niche Discovery Platform")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize Supabase client
supabase = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY
)

@app.get("/")
async def home(request: Request):
    """Home page route"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/startup/{id}")
async def startup_detail(request: Request, id: str):
    """Startup detail page route - uses localStorage data via JavaScript"""
    try:
        if not id or id == "undefined":
            raise HTTPException(status_code=400, detail="Invalid startup ID")
            
        print(f"Serving detail page for startup ID: {id}")
        
        # Return template that will be populated by JavaScript from localStorage
        # This avoids database lookup complexity and 404 errors
        return templates.TemplateResponse("startup_detail.html", {
            "request": request,
            "startup_id": id,
            "startup": {
                "id": id,
                "name": "Loading Startup Details...",
                "tagline": "Fetching data...",
                "problem_statement": ["Loading problem statement..."],
                "solution_highlights": ["Loading solution..."],
                "pain_points": ["Loading pain points..."],
                "competitive_advantages": ["Loading advantages..."],
                "metrics": {
                    "market_size": 1000000,
                    "growth_potential": 25,
                    "innovation_score": 70,
                    "competition_level": 50
                },
                "target_market": {
                    "size": 1000000,
                    "segments": ["Loading..."],
                    "geography": "Global",
                    "growth_rate": "25%"
                },
                "financial_projections": {
                    "year1": 500000,
                    "year2": 1000000,
                    "year3": 2000000
                },
                "technology_stack": {
                    "core_technologies": ["Loading..."],
                    "infrastructure": ["Loading..."]
                },
                "agentic_insights": {
                    "confidence_score": 0.8,
                    "generated_by_agents": ["AI System"]
                }
            }
        })
        
    except Exception as e:
        print(f"Error in startup detail: {e}")
        raise HTTPException(status_code=404, detail=f"Startup with ID {id} not found")

# Clean startup_detail function complete

# Clean startup_detail function complete

@app.post("/niche/{keyword}")
async def analyze_niche(keyword: str):
    try:
        data = await process_niche_analysis(keyword)
        
        # Use the niche ideas from the analysis as startup ideas
        startup_ideas = data.get('niche_ideas', [])
        
        # If no niche ideas generated, create a default one
        if not startup_ideas:
            idea_name = f"{keyword.capitalize()}Niche1"
            startup_ideas = [{
                'id': f"{keyword}-niche-1",
                'name': idea_name,
                'metrics': {
                    'market_size': data['market_data']['market_size'] * 1000,
                    'growth_potential': data['market_data']['growth_potential'],
                    'competition_level': data['market_data']['competition_level'],
                    'innovation_score': 70.0,
                    'user_demand': 60.0,
                    'profit_margin': 50.0,
                    'acquisition_cost': 500.0,
                    'lifetime_value': 2500.0
                },
                'tagline': f'Revolutionary solution for {keyword}',
                'description': f'Innovative platform addressing key challenges in the {keyword} market',
                'target_market': {
                    'segments': ['SMB', 'Enterprise'],
                    'size': data['market_data']['market_size'] * 1000,
                    'geography': 'Global',
                    'growth_rate': f"{data['market_data']['growth_potential']}% YoY"
                },
                'financial_projections': {
                    'year1': 500000.0,
                    'year2': 1000000.0,
                    'year3': 2000000.0
                },
                'funding_requirements': {
                    'seed_round': 250000.0,
                    'runway': 18.0
                },
                'technology_stack': {
                    'core_technologies': ['Python', 'React', 'PostgreSQL'],
                    'infrastructure': ['AWS', 'Docker']
                },
                'solution_highlights': [
                    f'AI-powered {keyword} platform',
                    'Scalable cloud infrastructure',
                    'Advanced analytics and reporting'
                ],
                'problem_statement': [
                    f'Current {keyword} solutions lack innovation',
                    'Users need more efficient tools',
                    'Market demands better integration'
                ]
            }]
            
        # Save to database for startup detail retrieval
        try:
            # Prepare data for database
            db_data = {
                'keyword': data['keyword'],
                'analysis_timestamp': data['analysis_timestamp'],
                'market_data': data['market_data'],
                'sentiment_analysis': data['sentiment_analysis'],
                'startup_ideas': startup_ideas,
                'niche_ideas': startup_ideas,  # Save both for compatibility
                'visualizations': data.get('visualizations', {}),
                'agentic_analysis': data.get('agentic_analysis', {})
            }
            
            # Save to Supabase
            async with httpx.AsyncClient() as client:
                db_response = await client.post(
                    f"{settings.SUPABASE_URL}/rest/v1/searches",
                    headers={
                        "apikey": settings.SUPABASE_KEY,
                        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "return=representation"
                    },
                    json=db_data
                )
                if db_response.status_code == 201:
                    print(f"✅ Saved {len(startup_ideas)} startup ideas to database for '{keyword}'")
                else:
                    print(f"⚠️ Failed to save to database: {db_response.status_code}")
                    
        except Exception as db_error:
            print(f"Database save error: {str(db_error)}")
            # Continue without failing the request
        
        # Ensure response data has the expected structure
        response_data = {
            'keyword': data['keyword'],
            'analysis_timestamp': data['analysis_timestamp'],
            'market_analysis': {
                'market_size': data['market_data']['market_size'],
                'growth_potential': data['market_data']['growth_potential'],
                'competition_level': data['market_data']['competition_level'],
                'opportunity_score': data['market_data'].get('opportunity_score', 75)
            },
            'sentiment_analysis': data['sentiment_analysis'],
            'startup_ideas': startup_ideas,  # This will display as "niche ideas" in the UI
            'visualizations': data.get('visualizations', {})
        }
        
        return JSONResponse(content=jsonable_encoder(response_data))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard():
    """Get the top searched niches with their metrics"""
    try:
        # Use direct async query with error handling
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.SUPABASE_URL}/rest/v1/searches",
                    headers={
                        "apikey": settings.SUPABASE_KEY,
                        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "return=representation"
                    },
                    params={
                        "select": "keyword,results,sentiment_analysis,market_data,analysis_timestamp",
                        "order": "analysis_timestamp.desc"
                    }
                )
                response.raise_for_status()
                result_data = response.json()
            
            if not result_data:
                print("Warning: No data from database")
                return []
                
        except httpx.HTTPError as e:
            print(f"HTTP error occurred: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error occurred: {str(e)}")
            return []
            
        # Process the data in memory
        keyword_stats = {}
        for row in result_data:
            keyword = row.get("keyword", "")
            if not keyword:
                continue
                
            # Initialize or update keyword stats
            if keyword not in keyword_stats:
                keyword_stats[keyword] = {
                    "search_count": 0,
                    "market_potential": 0.0,
                    "last_searched": row.get("analysis_timestamp"),
                    "sentiment_analysis": row.get("sentiment_analysis", {}),
                    "market_data": row.get("market_data", {})
                }
            
            stats = keyword_stats[keyword]
            stats["search_count"] += 1
            
            # Update last searched time if newer
            if row.get("analysis_timestamp") > stats["last_searched"]:
                stats["last_searched"] = row.get("analysis_timestamp")
                stats["sentiment_analysis"] = row.get("sentiment_analysis", {})
                stats["market_data"] = row.get("market_data", {})
        
        # Transform the data into LeaderboardEntry objects
        leaderboard = []
        for keyword, stats in keyword_stats.items():
            try:
                # Prepare success metrics
                success_metrics = {
                    "searches": stats["search_count"],
                    "last_analyzed": stats["last_searched"],
                    "sentiment_score": float(stats["sentiment_analysis"].get("overall_sentiment", 0)),
                    "market_size": float(stats["market_data"].get("market_size", 0)),
                    "growth_rate": stats["market_data"].get("growth_rate", "0%"),
                    "competition_level": float(stats["market_data"].get("competition_level", 50))
                }

                # Convert timestamp string to datetime if it's a string
                last_searched = (
                    datetime.fromisoformat(stats["last_searched"].replace("Z", "+00:00"))
                    if isinstance(stats["last_searched"], str)
                    else stats["last_searched"]
                )
                
                entry = LeaderboardEntry(
                    keyword=str(keyword),
                    search_count=int(stats["search_count"]),
                    market_potential=float(stats["market_data"].get("market_size", 50)),
                    success_metrics=success_metrics,
                    last_searched=last_searched
                )
                leaderboard.append(entry)
            except (ValueError, TypeError, KeyError) as e:
                print(f"Error processing leaderboard entry for {keyword}: {str(e)}")
                continue
        
        return sorted(leaderboard, key=lambda x: (-x.market_potential, -x.search_count))
        
    except Exception as e:
        print(f"Leaderboard error: {str(e)}")
        return []


