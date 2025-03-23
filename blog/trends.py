from pytrends.request import TrendReq
import os
import sys
import requests
import json
from collections import Counter
import re
from datetime import datetime, timedelta

# Import our content analyzer as a fallback
try:
    from blog.content_analyzer import extract_trending_topics, get_related_topics as get_related_topics_local
except ImportError:
    # Handle relative import
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from blog.content_analyzer import extract_trending_topics, get_related_topics as get_related_topics_local

# Default topics if API requests fail
DEFAULT_TOPICS = [
    "Artificial Intelligence", "Machine Learning", "Climate Change",
    "Blockchain", "Cryptocurrency", "Remote Work", "Mental Health",
    "Space Exploration", "Quantum Computing", "Renewable Energy",
    "Virtual Reality", "Augmented Reality", "Cybersecurity",
    "Social Media", "Data Privacy", "Internet of Things",
    "Cloud Computing", "Digital Transformation", "Healthcare Innovation",
    "Autonomous Vehicles"
]

def _extract_keywords_from_text(text, min_length=4):
    """Extract meaningful keywords from text."""
    # Remove special characters and convert to lowercase
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Split into words
    words = text.split()
    
    # Filter out short words and common stop words
    stop_words = {'the', 'and', 'is', 'in', 'to', 'of', 'for', 'a', 'on', 'with', 
                 'as', 'by', 'at', 'from', 'an', 'it', 'this', 'that', 'are', 
                 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 
                 'do', 'does', 'did', 'but', 'or', 'not', 'what', 'all', 'their'}
    
    filtered_words = [word for word in words 
                     if len(word) >= min_length and word not in stop_words]
    
    return filtered_words

def get_trending_topics_from_newsapi(query="technology", limit=20):
    """Get trending topics from NewsAPI.org using the /everything endpoint."""
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        print("Warning: NEWSAPI_KEY not found in environment variables.")
        return []
    
    # Calculate date range for recent articles
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    url = f"https://newsapi.org/v2/everything?q={query}&from={yesterday}&to={today}&sortBy=popularity&pageSize=30&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('status') != 'ok':
            print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            return []
        
        # Extract headlines and descriptions
        articles = data.get('articles', [])
        all_text = ""
        
        for article in articles:
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            if title:
                all_text += title + " "
            if description:
                all_text += description + " "
            if content:
                all_text += content + " "
        
        # Extract keywords
        keywords = _extract_keywords_from_text(all_text)
        
        # Count keyword frequency
        keyword_counter = Counter(keywords)
        
        # Get most common keywords
        common_keywords = [keyword for keyword, _ in keyword_counter.most_common(limit*2)]
        
        # Capitalize keywords
        topics = [keyword.capitalize() for keyword in common_keywords]
        
        # Remove duplicates while preserving order
        unique_topics = []
        for topic in topics:
            if topic not in unique_topics:
                unique_topics.append(topic)
        
        return unique_topics[:limit]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def get_trending_topics_from_gnews(query="", limit=20):
    """Get trending topics from GNews."""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Ensure query is never empty
        safe_query = query if query.strip() else "technology"
        
        # Build URL for gnews
        url = f"https://gnews.io/api/v4/search?q={safe_query}&from={yesterday}&to={today}&lang=en&max=10"
        api_key = os.getenv("GNEWS_API_KEY")
        
        if api_key:
            url += f"&apikey={api_key}"
        else:
            print("Warning: GNEWS_API_KEY not found in environment variables. Using limited access.")
        
        response = requests.get(url)
        data = response.json()
        
        if 'articles' not in data:
            print(f"GNews API error: {data.get('errors', ['Unknown error'])}")
            return []
        
        # Extract titles and descriptions
        articles = data.get('articles', [])
        all_text = ""
        
        for article in articles:
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            if title:
                all_text += title + " "
            if description:
                all_text += description + " "
            if content:
                all_text += content + " "
        
        # Extract keywords
        keywords = _extract_keywords_from_text(all_text)
        
        # Count keyword frequency
        keyword_counter = Counter(keywords)
        
        # Get most common keywords
        common_keywords = [keyword for keyword, _ in keyword_counter.most_common(limit*2)]
        
        # Capitalize keywords
        topics = [keyword.capitalize() for keyword in common_keywords]
        
        # Remove duplicates while preserving order
        unique_topics = []
        for topic in topics:
            if topic not in unique_topics:
                unique_topics.append(topic)
        
        return unique_topics[:limit]
    except Exception as e:
        print(f"Error fetching from GNews: {e}")
        return []

def get_trending_topics(country="us", limit=20):
    """Fetch trending topics from multiple sources."""
    topics = []
    
    # Try NewsAPI with technology query
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if newsapi_key and not newsapi_key.startswith('pub_'):
        topics = get_trending_topics_from_newsapi(query="technology trends", limit=limit)
    else:
        print("Skipping NewsAPI - key not found or invalid format")
    
    # Fallback to GNews
    if len(topics) < limit and os.getenv("GNEWS_API_KEY"):
        gnews_topics = get_trending_topics_from_gnews(query="emerging technologies", limit=limit)
        
        # Add unique GNews topics
        for topic in gnews_topics:
            if topic not in topics:
                topics.append(topic)
                if len(topics) >= limit:
                    break
    
    # Final fallbacks
    if len(topics) < 5:
        print("Using content analyzer as API requests failed or no API keys provided.")
        local_topics = extract_trending_topics(None, limit=limit)
        topics += [t for t in local_topics if t not in topics][:limit-len(topics)]
    
    if not topics:
        print("Using default topics as all methods failed.")
        topics = DEFAULT_TOPICS[:limit]
    
    return topics[:limit]

def get_related_topics(query, limit=5):
    """Get topics related to a specific query from news sources."""
    related_topics = []
    
    # Try GNews first
    if os.getenv("GNEWS_API_KEY"):
        safe_query = query if query.strip() else "technology innovations"
        related_topics = get_trending_topics_from_gnews(query=safe_query, limit=limit)
    
    # Fallback to NewsAPI
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if len(related_topics) < limit and newsapi_key and not newsapi_key.startswith('pub_'):
        news_topics = get_trending_topics_from_newsapi(query=query, limit=limit)
        related_topics += [t for t in news_topics if t not in related_topics][:limit-len(related_topics)]
    
    # Final fallbacks
    if len(related_topics) < 3:
        print("Using content analyzer for related topics")
        local_related = get_related_topics_local(query, limit)
        related_topics += [t for t in local_related if t not in related_topics][:limit-len(related_topics)]
    
    if not related_topics:
        print(f"Using default topics related to '{query}'")
        related_topics = DEFAULT_TOPICS[:limit]
    
    return related_topics[:limit]

def update_trending_keywords():
    """Update the agent's trending keywords with topics fetched from news sources."""
    topics = get_trending_topics()
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from agent.tools import update_keyword_list
    updated = update_keyword_list(topics)
    return updated

if __name__ == "__main__":
    print("Fetching trending topics from news sources...")
    topics = get_trending_topics()
    print("Trending Topics:")
    for topic in topics:
        print(f"- {topic}")
    
    print("\nUpdating agent's trending keywords...")
    updated_keywords = update_trending_keywords()
    print("Updated Trending Keywords:")
    for keyword in updated_keywords:
        print(f"- {keyword}")
    
    # Test related topics
    test_query = "Artificial Intelligence"
    print(f"\nFetching topics related to '{test_query}'...")
    related = get_related_topics(test_query)
    if related:
        print(f"Topics related to '{test_query}':")
        for topic in related:
            print(f"- {topic}")
    else:
        print(f"No related topics found for '{test_query}'")
