import httpx
import json
import re
from typing import Dict, Any
from pydantic import ValidationError
from config import settings

# Constants
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MAX_CORPUS_LENGTH = 5000  # Maximum length for market data in prompt
REQUEST_TIMEOUT = 30.0  # Timeout for API requests in seconds

# Get model configuration from settings
MODEL_NAME = settings.GROQ_PRIMARY_MODEL
BACKUP_MODELS = [settings.GROQ_BACKUP_MODEL]
MAX_TOKENS = settings.GROQ_MAX_TOKENS
MAX_TOKENS = 1024  # Maximum tokens for response
MAX_TOKENS = 1024  # Maximum tokens for response

class NicheAnalysis:
    @staticmethod
    def model_validate(data):
        # Mock validation - in real implementation this would be a Pydantic model
        required_keys = {
            "market_overview", "pain_points", "opportunities", 
            "trend_analysis", "market_segments", "competitor_analysis", 
            "visualization_data"
        }
        if not all(key in data for key in required_keys):
            raise ValidationError("Missing required keys")
        return data
    
    @staticmethod
    def model_dump():
        return {}

NICHE_ANALYSIS_PROMPT = """Analyze the {keyword} market and provide a COMPLETE market analysis.

Your response must be VALID JSON matching this EXACT structure:
{{
    "market_overview": {{"market_size": <float>, "growth_rate": <float>, "competition_index": <float 0-100>, "trend_sentiment": <float 0-100>, "opportunity_score": <float 0-100>}},
    "pain_points": [
        {{"description": "<str>", "severity": <int 1-10>, "frequency": "daily/weekly/monthly", "impact_score": <float 0-100>, "user_segment": "<str>", "validation_metrics": {{"metric": <float>}}}}
    ],
    "opportunities": [
        {{"name": "<str>", "description": "<str>", "pain_point_solved": "<str>", "competition_level": "Low|Medium|High", "growth_score": <int 1-10>, "real_world_impact": "<str>", "target_audience": ["<str>"], "revenue_streams": ["<str>"], "key_metrics": {{"market_potential": <float 0-100>, "execution_complexity": <float 0-100>, "resource_requirements": <float 0-100>, "time_to_market": <int months>, "roi_estimate": <float>, "risk_factors": {{"factor": <float>}}}}, "market_validation": {{"metric": <float>}}, "competitive_advantage": ["<str>"], "implementation_phases": {{"phase1": {{"name": "<str>", "duration": "<str>"}}}, "phase2": {{"name": "<str>", "duration": "<str>"}}}}}}
    ],
    "trend_analysis": {{"trend_name": [<float>]}}",
    "market_segments": {{"segment_name": {{"size": <float>, "growth": <float>}}}}",
    "competitor_analysis": [
        {{"name": "<str>", "market_share": <float>, "strengths": ["<str>"]}}
    ],
    "visualization_data": {{"chart_name": "<str>"}}}
}}


Requirements:
1. EXACTLY 3 opportunities with ALL fields filled out
2. Include market overview with ALL metrics
3. At least 3 pain points with ALL required fields
4. Competition levels must be exactly "Low", "Medium", or "High"
5. All numeric scores must be within specified ranges
6. ALL arrays must be properly populated
7. ALL nested objects must be complete

Remember: ONLY respond with the JSON object. NO other text.
"""

def create_default_response():
    """Create a default response structure with placeholder data."""
    default_pain_points = [ {
        "description": "Default market challenge",
        "severity": 7,
        "frequency": "regularly",
        "impact_score": 70.0,
        "user_segment": "General Market",
        "validation_metrics": {"confidence": 0.7}
    }] * 3
    
    competition_levels = ["Low", "Medium", "High"]
    default_opportunities = [
        {
            "name": f"Market Solution {i+1}",
            "description": f"Strategic market opportunity {i+1}",
            "pain_point_solved": "Market inefficiency",
            "competition_level": level,
            "growth_score": 8-i,
            "real_world_impact": "Market improvement",
            "target_audience": ["Early Adopters"],
            "revenue_streams": ["Subscription"],
            "key_metrics": {
                "market_potential": 80.0,
                "execution_complexity": 50.0,
                "resource_requirements": 60.0,
                "time_to_market": 6,
                "roi_estimate": 200.0,
                "risk_factors": {"competition": 0.5}
            },
            "market_validation": {"confidence": 0.8},
            "competitive_advantage": ["Innovation"],
            "implementation_phases": {
                "phase1": {"name": "Development", "duration": "3 months"},
                "phase2": {"name": "Launch", "duration": "3 months"}
            }
        }
        for i, level in enumerate(competition_levels)
    ]
    
    default_competitors = [
        {
            "name": f"Competitor {i+1}",
            "market_share": 20.0,
            "strengths": ["Market presence"]
        }
        for i in range(3)
    ]
    
    return {
        "market_overview": {
            "market_size": 1000000000.0,
            "growth_rate": 10.0,
            "competition_index": 50.0,
            "trend_sentiment": 75.0,
            "opportunity_score": 80.0
        },
        "pain_points": default_pain_points,
        "opportunities": default_opportunities,
        "trend_analysis": {"growth": [5.0, 7.0, 10.0, 12.0]},
        "market_segments": {
            "primary": {"size": 1000000000.0, "growth": 15.0},
            "secondary": {"size": 500000000.0, "growth": 8.0}
        },
        "competitor_analysis": default_competitors,
        "visualization_data": {
            "market_overview": "base64_chart_placeholder"
        }
    }

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
    text = re.sub(r'#{1,6}\s*', '', text)           # Headers
    text = re.sub(r'^\s*[-•*]\s*', '', text, flags=re.MULTILINE)  # Bullets
    text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)  # Numbers
    text = re.sub(r'\s+', ' ', text)                # Multiple spaces
    return text.strip()

def extract_field_value(text: str, field_patterns: list) -> str:
    """Extract field value using multiple patterns."""
    for pattern in field_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).strip()
            return clean_text(value)
    return ""

def extract_numeric_value(text: str, field_patterns: list, default: int) -> int:
    """Extract numeric value from text."""
    for pattern in field_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                value = int(match.group(1))
                return max(1, min(10, value))  # Clamp between 1-10
            except ValueError:
                continue
    return default

def parse_text_response(text: str) -> Dict[str, Any]:
    """Parse structured text response into JSON format with improved logic."""
    # Handle empty or whitespace-only responses
    if not text or not text.strip():
        print("Empty response received")
        return create_default_response()
    
    # Handle safety filter responses
    safety_indicators = ["safe", "unsafe", "content_policy", "safety_filter", "harmful_content"]
    if text.strip().lower() in safety_indicators:
        print(f"Safety filter response detected: {text.strip()}")
        return create_default_response()
    
    # Try to parse as direct JSON first
    try:
        # Look for JSON in code blocks first
        json_match = re.search(r'\`\`\`(?:json)?\s*(\{.*?\})\s*\`\`\`', text, re.DOTALL)
        if json_match:
            raw_json = json_match.group(1)
        else:
            # Try to extract JSON from the response more aggressively
            # Look for the first { and last } to capture the JSON object
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                raw_json = text[start_idx:end_idx + 1]
            else:
                # No JSON structure found, fall back to text parsing
                print("No JSON structure found in response")
                raise json.JSONDecodeError("No JSON found", text, 0)
        
        raw_json = raw_json.strip()
        if not raw_json.startswith('{') or not raw_json.endswith('}'):
            raise json.JSONDecodeError("Invalid JSON structure", raw_json, 0)
        
        parsed = json.loads(raw_json)
        
        # Verify we have required root keys
        required_keys = {
            "market_overview", "pain_points", "opportunities",
            "trend_analysis", "market_segments", "competitor_analysis",
            "visualization_data"
        }
        
        if all(key in parsed for key in required_keys):
            # Validate with Pydantic
            NicheAnalysis.model_validate(parsed)
            return parsed
        else:
            missing_keys = required_keys - set(parsed.keys())
            print(f"Missing required keys: {missing_keys}")
            raise ValidationError(f"Missing keys: {missing_keys}")
            
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Failed to parse JSON directly: {e}")
        print(f"Response content preview: {text[:500]}...")
    
    return parse_fallback_text(text)

def parse_fallback_text(text: str) -> Dict[str, Any]:
    """Enhanced fallback parsing for non-JSON responses."""
    print("Using fallback text parsing")
    
    pain_points = []
    opportunities = []
    
    # Split content into major sections more reliably
    sections = re.split(r'\n\s*(?=(?:PAIN\s+POINTS?|BUSINESS\s+OPPORTUNITIES?|OPPORTUNITIES?))', 
                       text, flags=re.IGNORECASE)
    
    pain_section = ""
    opp_section = ""
    
    for section in sections:
        section_lower = section.lower()
        if 'pain' in section_lower and 'point' in section_lower:
            pain_section = section
        elif 'opportunit' in section_lower or 'business' in section_lower:
            opp_section = section
    
    # Parse pain points with better error handling
    if pain_section:
        pain_blocks = re.split(r'\n\s*(?=\d+\.|\*\*|\w+:)', pain_section)
        
        for block in pain_blocks:
            if len(block.strip()) < 20:  # Skip short blocks
                continue
            
            # Extract description
            description_patterns = [
                r'(?:description[:\s]*)?([^:\n]{30,200})',
                r'^([^:\n]{20,200})',
            ]
            description = extract_field_value(block, description_patterns)
            
            if not description:
                continue
            
            # Extract severity
            severity_patterns = [
                r'severity[:\s]*(\d+)',
                r'(\d+)(?:/10|\s*out\s*of\s*10)',
                r'rating[:\s]*(\d+)'
            ]
            severity = extract_numeric_value(block, severity_patterns, 7)
            
            # Extract frequency
            frequency_patterns = [
                r'frequency[:\s]*(daily|weekly|monthly|regularly|constantly|frequently|rarely)',
                r'occurs?\s+(daily|weekly|monthly|regularly|constantly|frequently|rarely)',
            ]
            frequency = extract_field_value(block, frequency_patterns) or "regularly"
            
            # Clean description of field labels
            description = re.sub(r'(?i)severity[:\s]*\d+[/\d]*', '', description)
            description = re.sub(r'(?i)frequency[:\s]*\w+', '', description)
            description = clean_text(description)
            
            if len(description) >= 20:
                pain_points.append({
                    "description": description[:200],
                    "severity": severity,
                    "frequency": frequency.lower()
                })
    
    # Parse opportunities with better error handling
    if opp_section:
        opp_blocks = re.split(r'\n\s*(?=\d+\.|\*\*[^*]+\*\*|[A-Z][^:\n]{5,30}:)', opp_section)
        
        for block in opp_blocks:
            if len(block.strip()) < 30:
                continue
            
            # Extract business name
            name_patterns = [
                r'(?:name[:\s]*)?([A-Z][A-Za-z\s]{5,50})(?:\s*:|\s*-|\n)',
                r'^\s*([A-Z][A-Za-z\s]{5,50})(?=\s*:|\s*-|\n)',
                r'\*\*([^*]{5,50})\*\*'
            ]
            name = extract_field_value(block, name_patterns)
            
            if not name:
                # Use first substantial capitalized phrase
                first_line = block.split('\n')[0].strip()
                if len(first_line) > 5 and first_line[0].isupper():
                    name = clean_text(first_line)[:50]
                else:
                    continue
            
            opportunities.append({
                "name": name[:50],
                "description": f"Strategic solution for {name}",
                "pain_point_solved": "Market inefficiency",
                "competition_level": "Medium",
                "growth_score": 7,
                "real_world_impact": "Market improvement"
            })
    
    # Ensure minimum required items
    while len(pain_points) < 3:
        idx = len(pain_points) + 1
        pain_points.append({
            "description": f"Market challenge #{idx} requiring attention",
            "severity": 6 + idx,
            "frequency": ["regularly", "weekly", "monthly"][idx - 1]
        })
    
    while len(opportunities) < 3:
        idx = len(opportunities) + 1
        opportunities.append({
            "name": f"Solution{idx}",
            "description": f"Strategic opportunity #{idx}",
            "pain_point_solved": "Market gap",
            "competition_level": ["Low", "Medium", "High"][(idx-1) % 3],
            "growth_score": 9 - idx,
            "real_world_impact": "Market improvement"
        })
    
    # Build complete analysis structure
    return build_complete_analysis(pain_points, opportunities)

def build_complete_analysis(pain_points: list, opportunities: list) -> Dict[str, Any]:
    """Build complete analysis structure from parsed components."""
    return {
        "market_overview": {
            "market_size": 1000000000.0,
            "growth_rate": 10.0,
            "competition_index": 50.0,
            "trend_sentiment": 75.0,
            "opportunity_score": 80.0
        },
        "pain_points": [{
            "description": p["description"],
            "severity": p["severity"],
            "frequency": p["frequency"],
            "impact_score": float(p["severity"]) * 10.0,
            "user_segment": "General Market",
            "validation_metrics": {"confidence": float(p["severity"]) / 10.0}
        } for p in pain_points[:3]],
        "opportunities": [{
            "name": o["name"],
            "description": o["description"],
            "pain_point_solved": o["pain_point_solved"],
            "competition_level": o["competition_level"],
            "growth_score": o["growth_score"],
            "real_world_impact": o["real_world_impact"],
            "target_audience": ["Early Adopters", "Tech-Savvy Users"],
            "revenue_streams": ["Subscription", "Premium Features"],
            "key_metrics": {
                "market_potential": float(o["growth_score"]) * 10.0,
                "execution_complexity": 50.0,
                "resource_requirements": 60.0,
                "time_to_market": 6,
                "roi_estimate": float(o["growth_score"]) * 20.0,
                "risk_factors": {"competition": 0.5}
            },
            "market_validation": {"confidence_score": float(o["growth_score"]) / 10.0},
            "competitive_advantage": ["Innovative Solution", "Market Timing"],
            "implementation_phases": {
                "phase1": {"name": "Research & Development", "duration": "3 months"},
                "phase2": {"name": "Launch & Scale", "duration": "6 months"}
            }
        } for o in opportunities[:3]],
        "trend_analysis": {"market_growth": [5.0, 7.0, 10.0, 12.0]},
        "market_segments": {
            "primary_market": {"size": 1000000000.0, "growth": 15.0},
            "secondary_market": {"size": 500000000.0, "growth": 8.0}
        },
        "competitor_analysis": [
            {
                "name": opp["name"],
                "market_share": float(opp["growth_score"]) * 5.0,
                "strengths": [opp["pain_point_solved"]]
            } for opp in opportunities[:3]
        ],
        "visualization_data": {"market_overview": "base64_encoded_chart_placeholder"}
    }

async def analyze_with_llm(keyword: str, corpus: str = "") -> Dict[str, Any]:
    """Send data to Groq API for analysis and return structured market analysis."""
    if not keyword:
        raise ValueError("Keyword cannot be empty")

    if not settings.GROQ_API_KEY:
        raise ValueError("Groq API key not configured")

    print(f"\n=== Starting Analysis ===")
    print(f"Keyword: {keyword}")
    print(f"Input data length: {len(corpus) if corpus else 0} characters")

    # Safely handle corpus
    safe_corpus = ""
    if corpus and isinstance(corpus, str):
        safe_corpus = corpus[:MAX_CORPUS_LENGTH]
        print(f"Truncated market data to {len(safe_corpus)} characters")

    # Create the prompt
    prompt = NICHE_ANALYSIS_PROMPT.format(keyword=keyword)
    if safe_corpus:
        prompt += f"\n\nMarket Research Context:\n{safe_corpus}"

    # Setup request headers
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        # Try each model in sequence
        for model in [MODEL_NAME] + BACKUP_MODELS:
            print(f"API Key present: True")
            print(f"Trying model: {model}")
            
            request_data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": MAX_TOKENS,
                "top_p": 1,
                "stream": False
            }

            try:
                response = await client.post(API_URL, headers=headers, json=request_data)
                
                if response.status_code == 200:
                    response_data = response.json()
                    print(f"Raw response from {model}: {str(response_data)[:200]}...")
                    
                    if not response_data.get("choices") or not response_data["choices"][0].get("message"):
                        print(f"Empty or invalid response structure from {model}")
                        continue
                        
                    content = response_data["choices"][0]["message"]["content"]
                    print(f"Success with model: {model}")
                    print(f"Response content: {content[:200]}...")
                    
                    if not content or not content.strip():
                        print(f"Empty content from {model}")
                        continue
                    
                    # Check for safety filter or content policy messages
                    if any(marker in content.lower() for marker in ["content_policy", "safety_filter", "harmful_content"]):
                        print(f"Content filtered by {model}'s safety system")
                        continue
                    
                    try:
                        parsed_data = parse_text_response(content)
                        return parsed_data
                    except Exception as e:
                        print(f"Parse error with {model}: {str(e)}")
                        continue

                # Handle model-specific errors
                if response.status_code in (400, 404) and "model" in response.text.lower():
                    print(f"Model {model} not available: {response.text}")
                    continue
                    
                # Other API errors
                response.raise_for_status()

            except httpx.HTTPStatusError as e:
                print(f"HTTP error with {model}: {str(e)}")
                continue
            except Exception as e:
                print(f"Unexpected error with {model}: {str(e)}")
                continue

        # All models failed
        print("All available models failed")
        return create_error_response("No working models available")

def create_error_response(error_msg: str) -> Dict[str, Any]:
    """Create error response with fallback opportunities."""
    return {
        "market_overview": {
            "market_size": 0.0,
            "growth_rate": 0.0,
            "competition_index": 0.0,
            "trend_sentiment": 0.0,
            "opportunity_score": 0.0
        },
        "pain_points": [
            {
                "description": error_msg,
                "severity": 8,
                "frequency": "api-error",
                "impact_score": 80.0,
                "user_segment": "System",
                "validation_metrics": {"confidence": 0.0}
            }
        ],
        "opportunities": [
            {
                "name": "API Error Recovery",
                "description": "Implement fallback analysis or retry mechanism",
                "pain_point_solved": "API reliability issues",
                "competition_level": "Low",
                "growth_score": 6,
                "real_world_impact": "Improved system reliability",
                "target_audience": ["Developers"],
                "revenue_streams": ["Service Improvement"],
                "key_metrics": {
                    "market_potential": 60.0,
                    "execution_complexity": 40.0,
                    "resource_requirements": 30.0,
                    "time_to_market": 2,
                    "roi_estimate": 150.0,
                    "risk_factors": {"technical": 0.3}
                },
                "market_validation": {"confidence": 0.7},
                "competitive_advantage": ["Reliability"],
                "implementation_phases": {
                    "phase1": {"name": "Error Handling", "duration": "1 month"},
                    "phase2": {"name": "Testing", "duration": "1 month"}
                }
            },
            {
                "name": "Local Processing Mode",
                "description": "Implement offline market analysis capabilities",
                "pain_point_solved": "API availability issues",
                "competition_level": "Medium",
                "growth_score": 7,
                "real_world_impact": "Improved reliability",
                "target_audience": ["Enterprise Users"],
                "revenue_streams": ["Enterprise Plans"],
                "key_metrics": {
                    "market_potential": 70.0,
                    "execution_complexity": 60.0,
                    "resource_requirements": 50.0,
                    "time_to_market": 3,
                    "roi_estimate": 200.0,
                    "risk_factors": {"complexity": 0.5}
                },
                "market_validation": {"confidence": 0.8},
                "competitive_advantage": ["Independence"],
                "implementation_phases": {
                    "phase1": {"name": "Local Engine", "duration": "2 months"},
                    "phase2": {"name": "Testing", "duration": "1 month"}
                }
            },
            {
                "name": "Multi-Model Support",
                "description": "Support multiple LLM providers and models",
                "pain_point_solved": "Model dependency issues",
                "competition_level": "High",
                "growth_score": 8,
                "real_world_impact": "Enhanced reliability",
                "target_audience": ["Enterprise Users"],
                "revenue_streams": ["Premium API Access"],
                "key_metrics": {
                    "market_potential": 80.0,
                    "execution_complexity": 70.0,
                    "resource_requirements": 60.0,
                    "time_to_market": 4,
                    "roi_estimate": 250.0,
                    "risk_factors": {"investment": 0.6}
                },
                "market_validation": {"confidence": 0.9},
                "competitive_advantage": ["Flexibility"],
                "implementation_phases": {
                    "phase1": {"name": "Integration", "duration": "2 months"},
                    "phase2": {"name": "Deployment", "duration": "2 months"}
                }
            }
        ],
        "trend_analysis": {"error_rate": [0.0]},
        "market_segments": {
            "error_recovery": {"size": 0.0, "growth": 0.0}
        },
        "competitor_analysis": [
            {
                "name": "Error State",
                "market_share": 0.0,
                "strengths": ["None"]
            }
        ],
        "visualization_data": {
            "error_chart": "error_placeholder"
        }
    }

async def generate_mock_market_data(keyword: str) -> Dict[str, Any]:
    """Generate AI-based market data using Groq's intelligence."""
    prompt = f"""As an AI market analyst in September 2025, create a detailed market analysis for {keyword}. 
    Provide realistic, current market insights in this exact JSON format:
    {{
        "market_data": {{
            "overview": "Detailed market description",
            "size": <realistic market size in USD>,
            "trends": [
                {{"name": "Trend name", "value": <float 0-100>}},
                {{"name": "Trend name", "value": <float 0-100>}},
                {{"name": "Trend name", "value": <float 0-100>}}
            ],
            "demographics": [
                {{"age_group": "age range", "percentage": <int 0-100>}},
                {{"age_group": "age range", "percentage": <int 0-100>}},
                {{"age_group": "age range", "percentage": <int 0-100>}}
            ],
            "competitors": [
                {{"name": "Real competitor name", "market_share": <float 0-100>}},
                {{"name": "Real competitor name", "market_share": <float 0-100>}},
                {{"name": "Real competitor name", "market_share": <float 0-100>}}
            ],
            "growth_factors": [
                {{"factor": "Growth driver", "impact": <float 0-10>}},
                {{"factor": "Growth driver", "impact": <float 0-10>}},
                {{"factor": "Growth driver", "impact": <float 0-10>}}
            ]
        }},
        "market_maturity": "Emerging|Growing|Mature|Declining",
        "geographic_distribution": {{
            "regions": [
                {{"name": "Region name", "market_share": <float 0-100>}},
                {{"name": "Region name", "market_share": <float 0-100>}}
            ]
        }},
        "key_challenges": [
            {{"challenge": "Market challenge", "severity": <float 0-10>}},
            {{"challenge": "Market challenge", "severity": <float 0-10>}}
        ],
        "timestamp": "2025-09-23",
        "data_quality": "ai_generated",
        "confidence_score": <float 0-1>
    }}


    Requirements:
    1. Use current 2025 market knowledge
    2. Include real competitor names and market shares
    3. Provide realistic market sizes and growth rates
    4. Consider global economic conditions
    5. Include emerging trends and technologies
    6. Base demographics on current population data
    7. Consider regulatory environment
    """
    
    try:
        analysis = await analyze_with_llm(keyword, prompt)
        return analysis if isinstance(analysis, dict) else json.loads(analysis)
    except Exception as e:
        print(f"Error generating market data: {str(e)}")
        # Return a minimal response on error
        return {
            "market_data": {
                "overview": f"Error analyzing {keyword} market",
                "size": 0,
                "trends": [{"name": "Data Unavailable", "value": 0}],
                "demographics": [{"age_group": "N/A", "percentage": 0}],
                "competitors": [{"name": "Data Unavailable", "market_share": 0}],
                "growth_factors": [{"factor": "Data Unavailable", "impact": 0}]
            },
            "timestamp": "2025-09-23",
            "data_quality": "error",
            "confidence_score": 0
        }

if __name__ == "__main__":
    import asyncio
    
    async def test_analysis():
        keyword = "AI Tools"
        corpus = "Sample market data about AI tools and their growing popularity..."
        result = await analyze_with_llm(keyword, corpus)
        print(json.dumps(result, indent=2))
    
    # Run the test
    asyncio.run(test_analysis())
