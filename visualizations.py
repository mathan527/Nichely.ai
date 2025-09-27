import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List, Any, Optional
import base64
from io import BytesIO
from collections import Counter
import numpy as np
from textblob import TextBlob

def analyze_reddit_sentiment(discussions: List[str]) -> Dict[str, Any]:
    """Analyze sentiment and key topics from Reddit discussions"""
    # Sentiment analysis
    sentiments = []
    for text in discussions:
        blob = TextBlob(text)
        sentiments.append(blob.sentiment.polarity)
    
    sentiment_counts = {
        'Positive': len([s for s in sentiments if s > 0.1]),
        'Neutral': len([s for s in sentiments if -0.1 <= s <= 0.1]),
        'Negative': len([s for s in sentiments if s < -0.1])
    }
    
    # Word frequency analysis (excluding common words)
    words = ' '.join(discussions).lower().split()
    stop_words = {'the', 'and', 'is', 'in', 'to', 'a', 'for', 'of', 'with', 'on'}
    word_freq = Counter(w for w in words if w not in stop_words and len(w) > 3)
    
    return {
        'sentiment_counts': sentiment_counts,
        'word_frequency': dict(word_freq.most_common(10))
    }

def generate_niche_opportunity_chart(pain_points: List[Dict[str, Any]]) -> str:
    """Generate an opportunity analysis chart for a specific niche"""
    try:
        # Clear any existing plots
        plt.close('all')
        
        # Create new figure
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # Extract metrics with error handling
        categories = ['Market Size', 'Growth Potential', 'Competition', 'Entry Barrier', 'Profit Margin']
        try:
            values = [
                float(pain_points[0].get('market_size', 50)),
                float(pain_points[0].get('growth_potential', 50)),
                100 - float(pain_points[0].get('competition_level', 50)),  # Invert competition
                100 - float(pain_points[0].get('entry_barrier', 50)),      # Invert barrier
                float(pain_points[0].get('profit_margin', 50))
            ]
        except (IndexError, ValueError, TypeError) as e:
            print(f"Error extracting metrics: {str(e)}, using default values")
            values = [50, 50, 50, 50, 50]  # Default values
        
        # Create radar chart
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        values = np.concatenate((values, [values[0]]))  # complete the loop
        angles = np.concatenate((angles, [angles[0]]))  # complete the loop
        
        # Plot data
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        
        plt.title('Niche Opportunity Analysis')
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return chart_data
        
    except Exception as e:
        print(f"Error generating opportunity chart: {str(e)}")
        # Create a simple default chart
        plt.figure(figsize=(8, 8))
        plt.text(0.5, 0.5, 'Chart Generation Error', horizontalalignment='center')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        chart_data = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return chart_data
    
    # Save to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    chart_data = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return chart_data

def generate_reddit_visualizations(discussions: List[str]) -> Dict[str, str]:
    """Generate visualizations for Reddit data analysis"""
    analysis = analyze_reddit_sentiment(discussions)
    charts = {}
    
    # 1. Sentiment Distribution Pie Chart
    plt.figure(figsize=(8, 8))
    plt.pie(
        analysis['sentiment_counts'].values(),
        labels=analysis['sentiment_counts'].keys(),
        autopct='%1.1f%%',
        colors=['#2ecc71', '#95a5a6', '#e74c3c']
    )
    plt.title('Sentiment Distribution in Discussions')
    
    # Save to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    charts['sentiment_pie'] = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    # 2. Word Frequency Bar Chart
    plt.figure(figsize=(12, 6))
    words = list(analysis['word_frequency'].keys())
    freqs = list(analysis['word_frequency'].values())
    
    plt.bar(words, freqs, color='#3498db')
    plt.xticks(rotation=45, ha='right')
    plt.title('Most Common Topics in Discussions')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    
    # Save to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    charts['word_freq'] = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return charts
    """Create a radar chart for opportunity metrics"""
    metrics = opportunity['key_metrics']
    
    categories = ['Market Potential', 'ROI Estimate', 'Time to Market', 
                 'Resource Requirements', 'Execution Complexity']
    values = [metrics['market_potential'], metrics['roi_estimate'], 
             100 - metrics['time_to_market']*10, # Normalize to 0-100
             100 - metrics['resource_requirements'],
             100 - metrics['execution_complexity']]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=opportunity['name']
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True
    )
    
    buffer = BytesIO()
    fig.write_image(buffer, format='png')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()

