-- OPTIMIZED DATABASE SCHEMA FOR NICHELY APP
-- Designed for: 20 Reddit discussions → 5 startup ideas → detailed analysis workflow

-- Drop existing tables and recreate with optimized structure
DROP TABLE IF EXISTS startup_ideas CASCADE;
DROP TABLE IF EXISTS searches CASCADE;
DROP MATERIALIZED VIEW IF EXISTS leaderboard_view CASCADE;

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main searches table - stores each keyword analysis session
CREATE TABLE searches (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    keyword TEXT NOT NULL,
    analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reddit_discussions_count INTEGER DEFAULT 20,
    total_startup_ideas INTEGER DEFAULT 5,
    
    -- Core analysis data
    market_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    sentiment_analysis JSONB DEFAULT '{}'::jsonb,
    visualizations JSONB DEFAULT '{}'::jsonb,
    agentic_analysis JSONB DEFAULT '{}'::jsonb,
    
    -- Performance constraints
    CONSTRAINT keyword_not_empty CHECK (length(trim(keyword)) > 0),
    CONSTRAINT valid_discussions_count CHECK (reddit_discussions_count > 0 AND reddit_discussions_count <= 50),
    CONSTRAINT valid_ideas_count CHECK (total_startup_ideas > 0 AND total_startup_ideas <= 10)
);

-- Dedicated startup_ideas table - stores individual startup ideas with fast lookup
CREATE TABLE startup_ideas (
    id TEXT PRIMARY KEY, -- e.g., "blockchain-idea-1", "fintech-idea-3"
    search_id UUID NOT NULL REFERENCES searches(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    idea_index INTEGER NOT NULL, -- 1, 2, 3, 4, 5
    
    -- Core startup data
    name TEXT NOT NULL,
    problem_statement TEXT[] NOT NULL DEFAULT '{}',
    pain_points TEXT[] NOT NULL DEFAULT '{}',
    solution TEXT[] NOT NULL DEFAULT '{}',
    target_market TEXT DEFAULT '',
    competitive_advantages TEXT[] NOT NULL DEFAULT '{}',
    
    -- Metrics for fast filtering/sorting
    market_size BIGINT DEFAULT 1000000,
    growth_potential DECIMAL(5,2) DEFAULT 25.0,
    innovation_score DECIMAL(5,2) DEFAULT 50.0,
    competition_level DECIMAL(5,2) DEFAULT 50.0,
    
    -- Agentic AI insights
    ai_confidence DECIMAL(4,3) DEFAULT 0.750,
    ai_reasoning TEXT DEFAULT '',
    generated_by_agents TEXT[] DEFAULT '{}',
    
    -- Full detailed data as JSONB for complex queries
    full_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Performance constraints
    CONSTRAINT valid_idea_index CHECK (idea_index >= 1 AND idea_index <= 10),
    CONSTRAINT valid_metrics CHECK (
        market_size >= 0 AND 
        growth_potential >= 0 AND growth_potential <= 100 AND
        innovation_score >= 0 AND innovation_score <= 100 AND
        competition_level >= 0 AND competition_level <= 100 AND
        ai_confidence >= 0 AND ai_confidence <= 1
    )
);

-- INDEXES FOR MAXIMUM PERFORMANCE

-- Primary lookup indexes
CREATE INDEX idx_searches_keyword ON searches (keyword);
CREATE INDEX idx_searches_timestamp ON searches (analysis_timestamp DESC);
CREATE INDEX idx_startup_ideas_keyword ON startup_ideas (keyword);
CREATE INDEX idx_startup_ideas_search_id ON startup_ideas (search_id);

-- Fast startup idea lookup by ID (most important for our 404 issue)
CREATE INDEX idx_startup_ideas_id_hash ON startup_ideas USING HASH (id);

-- Composite indexes for common queries
CREATE INDEX idx_startup_ideas_keyword_timestamp ON startup_ideas (keyword, created_at DESC);
CREATE INDEX idx_startup_ideas_metrics ON startup_ideas (market_size DESC, growth_potential DESC);

-- JSONB indexes for complex queries
CREATE INDEX idx_searches_market_data_gin ON searches USING gin (market_data);
CREATE INDEX idx_startup_ideas_full_data_gin ON startup_ideas USING gin (full_data);

-- OPTIMIZED LEADERBOARD VIEW
CREATE MATERIALIZED VIEW leaderboard_view AS
SELECT 
    s.keyword,
    COUNT(s.id) as search_count,
    AVG(si.market_size * si.growth_potential / 100) as market_potential,
    jsonb_build_object(
        'searches', COUNT(s.id),
        'last_analyzed', MAX(s.analysis_timestamp),
        'avg_market_size', AVG(si.market_size),
        'avg_growth_rate', AVG(si.growth_potential),
        'avg_competition', AVG(si.competition_level),
        'avg_ai_confidence', AVG(si.ai_confidence),
        'total_ideas', COUNT(si.id)
    ) as success_metrics,
    MAX(s.analysis_timestamp) as last_searched
FROM searches s
LEFT JOIN startup_ideas si ON s.id = si.search_id
GROUP BY s.keyword
ORDER BY market_potential DESC, search_count DESC;

-- Unique index for concurrent refresh
CREATE UNIQUE INDEX idx_leaderboard_view_keyword ON leaderboard_view (keyword);

-- FAST LOOKUP FUNCTIONS

-- Get startup idea by ID (fixes our 404 issue)
CREATE OR REPLACE FUNCTION get_startup_by_id(startup_id TEXT)
RETURNS TABLE (
    id TEXT,
    name TEXT,
    problem_statement TEXT[],
    pain_points TEXT[],
    solution TEXT[],
    target_market TEXT,
    competitive_advantages TEXT[],
    market_size BIGINT,
    growth_potential DECIMAL,
    innovation_score DECIMAL,
    competition_level DECIMAL,
    ai_confidence DECIMAL,
    ai_reasoning TEXT,
    generated_by_agents TEXT[],
    full_data JSONB,
    keyword TEXT,
    search_timestamp TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        si.id,
        si.name,
        si.problem_statement,
        si.pain_points,
        si.solution,
        si.target_market,
        si.competitive_advantages,
        si.market_size,
        si.growth_potential,
        si.innovation_score,
        si.competition_level,
        si.ai_confidence,
        si.ai_reasoning,
        si.generated_by_agents,
        si.full_data,
        si.keyword,
        s.analysis_timestamp
    FROM startup_ideas si
    JOIN searches s ON si.search_id = s.id
    WHERE si.id = startup_id
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Get all startup ideas for a keyword (for frontend display)
CREATE OR REPLACE FUNCTION get_startup_ideas_by_keyword(search_keyword TEXT)
RETURNS TABLE (
    id TEXT,
    name TEXT,
    problem_statement TEXT[],
    pain_points TEXT[],
    market_size BIGINT,
    growth_potential DECIMAL,
    ai_confidence DECIMAL,
    idea_index INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        si.id,
        si.name,
        si.problem_statement,
        si.pain_points,
        si.market_size,
        si.growth_potential,
        si.ai_confidence,
        si.idea_index
    FROM startup_ideas si
    JOIN searches s ON si.search_id = s.id
    WHERE si.keyword = search_keyword
    ORDER BY s.analysis_timestamp DESC, si.idea_index ASC
    LIMIT 5;
END;
$$ LANGUAGE plpgsql;

-- Optimized leaderboard function
CREATE OR REPLACE FUNCTION get_leaderboard_data()
RETURNS TABLE (
    keyword TEXT,
    search_count BIGINT,
    market_potential DOUBLE PRECISION,
    success_metrics JSONB,
    last_searched TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM leaderboard_view
    ORDER BY market_potential DESC, search_count DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- TRIGGER FOR AUTO-REFRESH LEADERBOARD
CREATE OR REPLACE FUNCTION refresh_leaderboard_view()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard_view;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER refresh_leaderboard_trigger
    AFTER INSERT OR UPDATE OR DELETE ON searches
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_leaderboard_view();

CREATE TRIGGER refresh_leaderboard_ideas_trigger
    AFTER INSERT OR UPDATE OR DELETE ON startup_ideas
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_leaderboard_view();

-- PERFORMANCE OPTIMIZATION SETTINGS
-- Increase work_mem for better sorting performance
-- SET work_mem = '256MB';

-- Initial refresh of materialized view
REFRESH MATERIALIZED VIEW leaderboard_view;

-- Add helpful comments for maintenance
COMMENT ON TABLE searches IS 'Main analysis sessions - one per keyword search';
COMMENT ON TABLE startup_ideas IS 'Individual startup ideas - exactly 5 per search session';
COMMENT ON FUNCTION get_startup_by_id(TEXT) IS 'Fast lookup for startup detail pages - fixes 404 issues';
COMMENT ON FUNCTION get_startup_ideas_by_keyword(TEXT) IS 'Get 5 startup ideas for frontend display';
COMMENT ON MATERIALIZED VIEW leaderboard_view IS 'Cached leaderboard data for fast loading';