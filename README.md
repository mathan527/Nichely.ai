# Nichely - AI-Powered Startup Idea Generator

An intelligent startup idea generator that combines Reddit market analysis with advanced agentic AI to discover and validate niche business opportunities.

## 🚀 Features

- **AI-Powered Idea Generation**: Advanced multi-agent AI system for comprehensive startup analysis
- **Market Intelligence**: Real-time Reddit data analysis for market insights
- **Agentic AI Agents**: Specialized AI agents for market research, business analysis, and validation
- **Interactive Visualizations**: Dynamic charts and graphs for market data
- **Detailed Analysis**: In-depth startup opportunity breakdowns with AI reasoning
- **Responsive Design**: Modern UI with Tailwind CSS

## 🏗️ Architecture

### Core Components
- **FastAPI Backend**: RESTful API with async support
- **Agentic AI System**: Multi-agent framework for intelligent analysis
- **Reddit Integration**: Live market data from Reddit communities
- **Visualization Engine**: Interactive charts with Plotly
- **Responsive Frontend**: Tailwind CSS with dynamic JavaScript

### AI Agent System
- **MarketResearchAgent**: Analyzes market trends and opportunities
- **BusinessAnalysisAgent**: Evaluates business viability and revenue models  
- **ValidationAgent**: Validates ideas against market and technical criteria
- **OrchestratorAgent**: Coordinates multi-agent workflows

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- OpenAI API key (for agentic AI features)
- Reddit API credentials (optional, has fallback data)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd nichely/app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```env
# OpenAI API (Required for Agentic AI)
OPENAI_API_KEY=your_openai_api_key_here

# GROQ API (Alternative to OpenAI)
GROQ_API_KEY=your_groq_api_key_here

# Reddit API (Optional - has fallback)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name

# Supabase (Optional - for data persistence)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 4. Run the Application
```bash
python main.py
```

Visit `http://localhost:8000` to access the application.

## 🤖 Agentic AI Configuration

The application features an advanced multi-agent AI system that provides enhanced analysis:

### API Key Setup
1. **OpenAI**: Get your API key from [OpenAI Platform](https://platform.openai.com/)
2. **GROQ**: Alternative LLM provider with faster inference at [GROQ](https://groq.com/)

### Agent Configuration
Agents can be customized in `agents/agentic_ai.py`:
- Model selection (GPT-4, GPT-3.5-turbo, GROQ models)
- Temperature and creativity settings
- Agent-specific prompts and behaviors
- Validation thresholds

### Fallback System
The application gracefully handles missing AI dependencies:
- Falls back to standard analysis without agentic features
- Maintains full functionality with basic AI
- Progressive enhancement with advanced agents

## 📊 Usage

### Basic Analysis
1. Enter a keyword or niche topic
2. Click "Analyze Niche" to generate ideas
3. View AI-generated startup opportunities
4. Click on any idea for detailed analysis

### Advanced Features
- **AI Reasoning**: View detailed AI analysis and confidence scores
- **Market Validation**: See multi-agent validation results
- **Interactive Charts**: Explore market data visualizations
- **Export Options**: Save analysis results (coming soon)

## 🧪 API Endpoints

### Core Endpoints
- `GET /` - Main application interface
- `GET /niche/{keyword}` - Analyze niche and generate ideas
- `GET /startup/{startup_id}` - Detailed startup analysis

### Data Format
```json
{
  "ideas": [
    {
      "name": "Startup Name",
      "tagline": "Brief description",
      "problem_statement": ["Problem 1", "Problem 2"],
      "solution_highlights": ["Solution 1", "Solution 2"],
      "competitive_advantage": "Key differentiator",
      "agentic_insights": {
        "confidence_score": 0.85,
        "generated_by_agents": ["MarketResearchAgent", "BusinessAnalysisAgent"],
        "market_research": {...},
        "business_analysis": {...},
        "validation": {...}
      },
      "ai_reasoning": "AI analysis explanation"
    }
  ]
}
```

## 🔧 Configuration

### Agent Settings
Modify `agents/agentic_ai.py` for custom agent behavior:
```python
# Model configuration
MODEL_NAME = "gpt-4"  # or "gpt-3.5-turbo", "mixtral-8x7b-32768"
TEMPERATURE = 0.7     # Creativity level (0.0-1.0)

# Agent-specific settings
MARKET_RESEARCH_DEPTH = "comprehensive"  # or "basic", "detailed"
VALIDATION_THRESHOLD = 0.6               # Minimum confidence score
```

### Reddit Integration
Configure Reddit data sources in `data_fetchers.py`:
```python
# Subreddits to analyze
TARGET_SUBREDDITS = [
    "entrepreneur", "startups", "smallbusiness",
    "SideProject", "EntrepreneurRideAlong"
]

# Analysis parameters
POST_LIMIT = 100        # Number of posts to analyze
TIME_FILTER = "week"    # "hour", "day", "week", "month", "year"
```

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
1. **Docker**: Use provided Dockerfile for containerization
2. **Environment**: Set production environment variables
3. **Scaling**: Configure load balancing for high traffic
4. **Monitoring**: Set up logging and error tracking

## 🧩 Project Structure

```
nichely/app/
├── main.py                 # FastAPI application entry point
├── analysis.py            # Core analysis engine
├── data_fetchers.py       # Reddit and data collection
├── llm.py                 # LLM integration and prompts
├── models.py              # Data models and schemas
├── visualizations.py      # Chart generation
├── config.py             # Configuration settings
├── agents/
│   └── agentic_ai.py     # Multi-agent AI system
├── templates/            # Jinja2 HTML templates
│   ├── index.html        # Main interface
│   ├── startup_detail.html # Detailed analysis view
│   └── startup_ideas.html  # Ideas listing
├── static/              # Static assets
│   ├── css/
│   │   └── styles.css   # Custom styles
│   └── js/
│       ├── niche-analysis.js    # Main frontend logic
│       └── startup-ideas.js     # Ideas interaction
└── requirements.txt     # Python dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔮 Roadmap

### Upcoming Features
- [ ] Advanced agent orchestration patterns
- [ ] Real-time collaboration features
- [ ] Integration with additional data sources
- [ ] Mobile-responsive enhancements
- [ ] Export functionality for analysis results
- [ ] Custom agent creation interface
- [ ] Market trend prediction models
- [ ] Competitive analysis automation

### Performance Improvements
- [ ] Caching layer for faster responses
- [ ] Async processing for large datasets
- [ ] Database optimization
- [ ] CDN integration for static assets

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: See inline code comments
- **Community**: Join our Discord server

## 🙏 Acknowledgments

- OpenAI for GPT models and LangChain integration
- Reddit API for market data access
- Plotly for interactive visualizations
- Tailwind CSS for responsive design
- FastAPI for high-performance backend

---

**Built with ❤️ for entrepreneurs and innovators**