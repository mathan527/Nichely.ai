from typing import Dict, List, Any
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from textblob import TextBlob
from datetime import datetime, timedelta

def generate_trend_chart(keyword: str, discussions: List[str]) -> str:
    """Generate a line chart showing topic trends over time"""
    try:
        plt.clf()
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Create time series data from discussions
        dates = [datetime.now() - timedelta(days=i) for i in range(30)]
        mentions = [sum(1 for d in discussions if keyword.lower() in d.lower()) for _ in range(30)]
        
        # Plot trend line
        ax.plot(dates, mentions, marker='o')
        ax.set_title(f'Trend Analysis: {keyword.title()}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Mentions')
        
        # Rotate date labels
        plt.xticks(rotation=45)
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(image_png).decode('utf-8')
    except Exception as e:
        print(f"Error generating trend chart: {str(e)}")
        return ""

def generate_competitor_chart(competitor_mentions: List[str]) -> str:
    """Generate a bar chart showing competitor analysis"""
    try:
        plt.clf()
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Extract competitor names and counts
        competitors = {}
        for mention in competitor_mentions:
            for word in mention.split():
                if len(word) > 3:  # Simple filter for company names
                    competitors[word] = competitors.get(word, 0) + 1
        
        # Get top competitors
        top_competitors = dict(sorted(competitors.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Create bar chart
        ax.bar(top_competitors.keys(), top_competitors.values())
        ax.set_title('Competitor Landscape')
        ax.set_xlabel('Competitors')
        ax.set_ylabel('Mentions')
        
        plt.xticks(rotation=45)
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(image_png).decode('utf-8')
    except Exception as e:
        print(f"Error generating competitor chart: {str(e)}")
        return ""

def generate_feature_impact_chart(feature_requests: List[str]) -> str:
    """Generate a bubble chart showing feature impact analysis"""
    try:
        plt.clf()
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Process feature requests
        features = {}
        for request in feature_requests:
            words = request.split()
            for word in words:
                if len(word) > 3:
                    features[word] = features.get(word, 0) + 1
        
        # Get top features
        top_features = dict(sorted(features.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Create horizontal bar chart
        y_pos = range(len(top_features))
        ax.barh(y_pos, list(top_features.values()))
        ax.set_yticks(y_pos)
        ax.set_yticklabels(list(top_features.keys()))
        ax.set_title('Feature Impact Analysis')
        ax.set_xlabel('Demand Score')
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(image_png).decode('utf-8')
    except Exception as e:
        print(f"Error generating feature impact chart: {str(e)}")
        return ""

def generate_enhanced_opportunity_chart(data: Dict) -> str:
    """Generate an enhanced radar chart for niche opportunities"""
    try:
        plt.clf()
        fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
        
        # Enhanced metrics
        metrics = ['Market Size', 'Growth', 'Innovation', 'Competition', 'Demand', 'Profit']
        values = [
            data['market_size'],
            data['growth_potential'],
            data['innovation_score'],
            data['competition_level'],
            data['user_demand'],
            data['profit_margin']
        ]
        
        # Number of variables
        num_vars = len(metrics)
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        angles += angles[:1]
        
        # Plot data with enhanced styling
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        
        # Customize chart
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 100)
        
        # Add grid
        ax.grid(True)
        
        # Add title
        plt.title('Enhanced Opportunity Analysis', pad=20)
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(image_png).decode('utf-8')
    except Exception as e:
        print(f"Error generating enhanced opportunity chart: {str(e)}")
        return ""

def analyze_reddit_sentiment(discussions: List[str]) -> Dict[str, Any]:
    """Analyze Reddit discussions to extract sentiment and insights"""
    # Initialize variables
    word_frequency = {}
    sentiment_scores = []
    common_topics = set()
    
    # Define stop words for filtering
    stop_words = {'the', 'and', 'is', 'in', 'to', 'a', 'for', 'of', 'with', 'on',
                 'at', 'from', 'by', 'was', 'were', 'this', 'that', 'but', 'they',
                 'have', 'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'}
    
    for discussion in discussions:
        # Analyze sentiment
        blob = TextBlob(discussion)
        sentiment_scores.append(blob.sentiment.polarity)
        
        # Process words
        words = discussion.lower().split()
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_frequency[word] = word_frequency.get(word, 0) + 1
                if word_frequency[word] > 2:  # Consider as common topic if mentioned more than twice
                    common_topics.add(word)
    
    # Calculate overall sentiment
    overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    # Calculate sentiment distribution
    sentiment_distribution = {
        'positive': len([s for s in sentiment_scores if s > 0.2]),
        'neutral': len([s for s in sentiment_scores if -0.2 <= s <= 0.2]),
        'negative': len([s for s in sentiment_scores if s < -0.2])
    }
    
    return {
        'word_frequency': word_frequency,
        'sentiment_scores': sentiment_scores,
        'overall_sentiment': overall_sentiment,
        'common_topics': list(common_topics),
        'sentiment_distribution': sentiment_distribution
    }

def generate_financial_projections_chart(metrics: Dict) -> str:
    """Generate a line chart showing financial projections"""
    try:
        plt.clf()
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Generate projection data
        years = range(4)  # 0 to 3 years
        base_revenue = metrics['market_size'] * metrics['user_demand'] / 100
        growth_rate = metrics['growth_potential'] / 100
        
        projections = [base_revenue * (1 + growth_rate) ** year for year in years]
        
        # Plot projections
        ax.plot(years, projections, marker='o', linewidth=2)
        ax.set_title('Financial Projections')
        ax.set_xlabel('Years')
        ax.set_ylabel('Projected Revenue ($)')
        ax.grid(True)
        
        # Format y-axis labels
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode('utf-8')
    except Exception as e:
        print(f"Error generating financial projections chart: {str(e)}")
        return ""