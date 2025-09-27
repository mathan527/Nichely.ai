-- Drop existing triggers and views to avoid conflicts
DROP TRIGGER IF EXISTS refresh_leaderboard_trigger ON searches;
DROP FUNCTION IF EXISTS refresh_leaderboard_view() CASCADE;
DROP MATERIALIZED VIEW IF EXISTS leaderboard_view;

-- Modify the searches table to better handle our current implementation
ALTER TABLE searches 
    ALTER COLUMN results SET DEFAULT '{}'::jsonb;

-- Add new columns if they don't exist
DO $$
BEGIN
    -- Add market_data if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name = 'searches' AND column_name = 'market_data') THEN
        ALTER TABLE searches ADD COLUMN market_data jsonb DEFAULT '{}'::jsonb;
    END IF;

    -- Add niche_ideas if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name = 'searches' AND column_name = 'niche_ideas') THEN
        ALTER TABLE searches ADD COLUMN niche_ideas jsonb[] DEFAULT ARRAY[]::jsonb[];
    END IF;

    -- Add sentiment_analysis if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name = 'searches' AND column_name = 'sentiment_analysis') THEN
        ALTER TABLE searches ADD COLUMN sentiment_analysis jsonb DEFAULT '{}'::jsonb;
    END IF;

    -- Add visualizations if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name = 'searches' AND column_name = 'visualizations') THEN
        ALTER TABLE searches ADD COLUMN visualizations jsonb DEFAULT '{}'::jsonb;
    END IF;
END $$;

-- Create indexes for JSON fields we frequently query if they don't exist
DO $$
BEGIN
    -- Create index for results if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_searches_results_gin') THEN
        CREATE INDEX idx_searches_results_gin ON searches USING gin (results);
    END IF;

    -- Create index for niche_ideas if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_searches_niche_ideas_gin') THEN
        CREATE INDEX idx_searches_niche_ideas_gin ON searches USING gin (niche_ideas);
    END IF;
END $$;

-- Create a more flexible leaderboard view that matches our current implementation
CREATE MATERIALIZED VIEW leaderboard_view AS
WITH latest_searches AS (
    SELECT DISTINCT ON (keyword)
        keyword,
        results,
        niche_ideas,
        sentiment_analysis,
        analysis_timestamp
    FROM searches
    ORDER BY keyword, analysis_timestamp DESC
),
aggregated_metrics AS (
    SELECT 
        ls.keyword,
        COUNT(*) OVER (PARTITION BY ls.keyword) as search_count,
        COALESCE(
            (SELECT AVG(
                (idea->>'potential_score')::float * 0.4 +
                (idea->'metrics'->>'market_size')::float * 0.3 +
                (idea->'metrics'->>'growth_potential')::float * 0.2 +
                (1 - (idea->'metrics'->>'competition_level')::float/100) * 0.1
            )
            FROM jsonb_array_elements(ls.results->'niche_ideas') idea
            WHERE idea->>'potential_score' IS NOT NULL
            ), 50.0
        ) as market_potential,
        jsonb_build_object(
            'searches', (SELECT COUNT(*) FROM searches s2 WHERE s2.keyword = ls.keyword),
            'last_analyzed', ls.analysis_timestamp,
            'sentiment_score', COALESCE((ls.sentiment_analysis->>'overall_sentiment')::float, 0),
            'growth_trend', COALESCE(ls.results->'market_overview'->>'growth_rate', '0')
        ) as success_metrics,
        ls.analysis_timestamp as last_searched
    FROM latest_searches ls
)
SELECT 
    keyword,
    search_count,
    market_potential,
    success_metrics,
    last_searched
FROM aggregated_metrics
ORDER BY market_potential DESC, search_count DESC;

-- Create a unique index on the materialized view for concurrent refresh
CREATE UNIQUE INDEX IF NOT EXISTS idx_leaderboard_view_keyword ON leaderboard_view (keyword);

-- Initial refresh of the materialized view
REFRESH MATERIALIZED VIEW leaderboard_view;

-- Create a more robust refresh function
CREATE OR REPLACE FUNCTION refresh_leaderboard_view()
RETURNS TRIGGER AS $$
BEGIN
    -- Only refresh if the change affects metrics we care about
    IF (TG_OP = 'INSERT') OR 
       (TG_OP = 'UPDATE' AND (
           OLD.results IS DISTINCT FROM NEW.results OR
           OLD.niche_ideas IS DISTINCT FROM NEW.niche_ideas OR
           OLD.sentiment_analysis IS DISTINCT FROM NEW.sentiment_analysis
       )) OR 
       (TG_OP = 'DELETE')
    THEN
        BEGIN
            -- Try concurrent refresh first
            REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard_view;
        EXCEPTION WHEN OTHERS THEN
            -- Fallback to regular refresh if concurrent fails
            REFRESH MATERIALIZED VIEW leaderboard_view;
        END;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Recreate the trigger with better concurrency handling
CREATE TRIGGER refresh_leaderboard_trigger
    AFTER INSERT OR UPDATE OR DELETE ON searches
    FOR EACH ROW
    EXECUTE FUNCTION refresh_leaderboard_view();

-- Create a function to clean up old search records while maintaining trends
CREATE OR REPLACE FUNCTION cleanup_old_searches()
RETURNS void AS $$
BEGIN
    -- Keep only the latest 5 searches per keyword from the last 30 days
    WITH ranked_searches AS (
        SELECT id,
        ROW_NUMBER() OVER (
            PARTITION BY keyword 
            ORDER BY analysis_timestamp DESC
        ) as rn
        FROM searches
        WHERE analysis_timestamp > (CURRENT_TIMESTAMP - INTERVAL '30 days')
    )
    DELETE FROM searches s
    WHERE s.id IN (
        SELECT id 
        FROM ranked_searches 
        WHERE rn > 5
    );
    
    -- Refresh the leaderboard view after cleanup
    REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard_view;
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled cleanup job (if using pg_cron extension)
-- Uncomment if pg_cron is available
-- SELECT cron.schedule('0 0 * * *', 'SELECT cleanup_old_searches()');

-- Drop existing functions if they exist
DROP FUNCTION IF EXISTS get_leaderboard_data();

-- Create the get_leaderboard_data function
CREATE OR REPLACE FUNCTION get_leaderboard_data()
RETURNS TABLE (
    keyword TEXT,
    search_count BIGINT,
    market_potential FLOAT,
    success_metrics JSONB,
    last_searched TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    WITH latest_searches AS (
        SELECT DISTINCT ON (searches.keyword)
            searches.keyword,
            searches.results,
            searches.niche_ideas,
            searches.sentiment_analysis,
            searches.market_data,
            searches.analysis_timestamp
        FROM searches
        ORDER BY searches.keyword, searches.analysis_timestamp DESC
    ),
    aggregated_metrics AS (
        SELECT 
            ls.keyword,
            COUNT(*) OVER (PARTITION BY ls.keyword) as search_count,
            COALESCE(
                (SELECT AVG(
                    (idea->>'market_size')::float * 0.4 +
                    (idea->>'growth_potential')::float * 0.3 +
                    (idea->>'innovation_score')::float * 0.2 +
                    (100 - (idea->>'competition_level')::float) * 0.1
                )
                FROM unnest(ls.niche_ideas) AS arr(idea)
                ), 50.0
            ) as market_potential,
            jsonb_build_object(
                'searches', (SELECT COUNT(*) FROM searches s2 WHERE s2.keyword = ls.keyword),
                'last_analyzed', ls.analysis_timestamp,
                'sentiment_score', COALESCE((ls.sentiment_analysis->>'overall_sentiment')::float, 0),
                'market_size', COALESCE((ls.market_data->>'market_size')::float, 0),
                'growth_rate', COALESCE(ls.market_data->>'growth_rate', '0%'),
                'competition_level', COALESCE((ls.market_data->>'competition_level')::float, 50)
            ) as success_metrics,
            ls.analysis_timestamp as last_searched
        FROM latest_searches ls
    )
    SELECT 
        am.keyword,
        am.search_count,
        am.market_potential,
        am.success_metrics,
        am.last_searched
    FROM aggregated_metrics am
    ORDER BY am.market_potential DESC, am.search_count DESC;
END;
$$ LANGUAGE plpgsql;