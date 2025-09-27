-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create searches table to store market analysis results
CREATE TABLE searches (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    keyword TEXT NOT NULL,
    results JSONB NOT NULL,
    market_data JSONB,
    stock_correlations JSONB,
    analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    analysis_depth INTEGER NOT NULL DEFAULT 1 CHECK (analysis_depth BETWEEN 1 AND 5),
    time_horizon INTEGER CHECK (time_horizon > 0 AND time_horizon <= 60),
    
    CONSTRAINT keyword_not_empty CHECK (length(keyword) > 0)
);

-- Create indexes for search optimization
CREATE INDEX idx_searches_keyword ON searches (keyword);
CREATE INDEX idx_searches_timestamp ON searches (analysis_timestamp);

-- Create a materialized view for leaderboard data
CREATE MATERIALIZED VIEW leaderboard_view AS
SELECT 
    keyword,
    COUNT(*) as search_count,
    AVG((results->'market_overview'->>'opportunity_score')::float) as market_potential,
    jsonb_object_agg(
        'metrics',
        jsonb_build_object(
            'avg_growth_rate', AVG((market_data->>'growth_rate')::float),
            'avg_market_size', AVG((market_data->>'market_size')::float),
            'avg_competition_index', AVG((results->'market_overview'->>'competition_index')::float)
        )
    ) as success_metrics,
    MAX(analysis_timestamp) as last_searched
FROM searches
GROUP BY keyword
ORDER BY search_count DESC, market_potential DESC;

-- Refresh the materialized view automatically
CREATE OR REPLACE FUNCTION refresh_leaderboard_view()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW leaderboard_view;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER refresh_leaderboard_trigger
AFTER INSERT OR UPDATE OR DELETE ON searches
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_leaderboard_view();