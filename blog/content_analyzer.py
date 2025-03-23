import re
from collections import Counter
import os
import sys
import random

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Default content categories for topic generation
TECHNOLOGY_TOPICS = [
    "Artificial Intelligence", "Machine Learning", "Blockchain",
    "Cybersecurity", "Cloud Computing", "Data Science", "Internet of Things",
    "Virtual Reality", "Augmented Reality", "5G Technology",
    "Quantum Computing", "Edge Computing", "Digital Transformation",
    "Robotics", "Autonomous Vehicles", "Smart Home", "Wearable Technology"
]

BUSINESS_TOPICS = [
    "Remote Work", "Digital Marketing", "E-commerce", "Startup Culture",
    "Leadership", "Innovation", "Entrepreneurship", "Sustainability",
    "Future of Work", "Business Strategy", "Project Management",
    "Supply Chain", "Customer Experience", "Financial Technology"
]

HEALTH_TOPICS = [
    "Mental Health", "Nutrition", "Fitness", "Medical Research",
    "Healthcare Technology", "Telemedicine", "Wellness", "Mindfulness",
    "Public Health", "Preventive Care", "Health Equity", "Biohacking"
]

SOCIETY_TOPICS = [
    "Social Media", "Climate Change", "Sustainability", "Education",
    "Future of Work", "Urban Planning", "Social Justice", "Privacy",
    "Data Ethics", "Community Building", "Digital Nomads", "Remote Learning"
]

ALL_CATEGORIES = {
    "Technology": TECHNOLOGY_TOPICS,
    "Business": BUSINESS_TOPICS,
    "Health": HEALTH_TOPICS,
    "Society": SOCIETY_TOPICS
}

def extract_keywords_from_text(text, min_length=4, max_words=3):
    """Extract meaningful keywords and phrases from text."""
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
    
    # Create a list of single keywords
    keywords = filtered_words
    
    # Also create 2-3 word phrases (to catch things like "machine learning")
    phrases = []
    for i in range(len(words) - 1):
        if words[i] not in stop_words and len(words[i]) >= min_length:
            # Two-word phrases
            phrases.append(f"{words[i]} {words[i+1]}")
            
            # Three-word phrases
            if i < len(words) - 2:
                phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
    
    return keywords + phrases

def extract_trending_topics(content, limit=10):
    """Extract trending topics from content."""
    if not content:
        return get_topics_for_category(None, limit)
    
    # Extract keywords from content
    keywords = extract_keywords_from_text(content)
    
    # Count keyword frequency
    keyword_counter = Counter(keywords)
    
    # Get most common keywords
    common_keywords = [keyword for keyword, _ in keyword_counter.most_common(limit*2)]
    
    # Clean up and capitalize
    topics = []
    for keyword in common_keywords:
        # Capitalize each word
        words = keyword.split()
        capitalized = ' '.join(word.capitalize() for word in words)
        topics.append(capitalized)
    
    # Remove duplicates while preserving order
    unique_topics = []
    for topic in topics:
        if topic not in unique_topics:
            unique_topics.append(topic)
    
    result = unique_topics[:limit]
    
    # If we don't have enough topics, supplement with defaults
    if len(result) < limit:
        # Determine which category most closely matches the content
        category = determine_content_category(content)
        additional_topics = get_topics_for_category(category, limit - len(result))
        
        # Add additional topics that aren't already in our list
        for topic in additional_topics:
            if topic not in result:
                result.append(topic)
    
    return result[:limit]

def determine_content_category(content):
    """Determine which category the content most closely matches."""
    if not content:
        return None
        
    # Convert content to lowercase for better matching
    content = content.lower()
    
    # Count matches for each category
    category_scores = {}
    
    for category, topics in ALL_CATEGORIES.items():
        score = 0
        for topic in topics:
            if topic.lower() in content:
                score += 3  # Exact match gets highest score
            else:
                # Check for individual words from the topic
                topic_words = topic.lower().split()
                for word in topic_words:
                    if len(word) > 3 and word in content:
                        score += 1
        
        category_scores[category] = score
    
    # Return the category with the highest score
    if category_scores:
        max_category = max(category_scores, key=category_scores.get)
        if category_scores[max_category] > 0:
            return max_category
    
    # If no clear category is found, return None
    return None

def get_topics_for_category(category, limit=10):
    """Get topics for a specific category."""
    if category and category in ALL_CATEGORIES:
        # Get topics from the specified category
        topics = ALL_CATEGORIES[category].copy()
    else:
        # If no category specified or not found, use a mix of topics
        topics = []
        for cat_topics in ALL_CATEGORIES.values():
            topics.extend(cat_topics)
    
    # Shuffle to get a random selection
    random.shuffle(topics)
    
    return topics[:limit]

def get_related_topics(query, limit=5):
    """Get topics related to a specific query."""
    # Check what category the query matches
    query_category = determine_content_category(query)
    
    # Get relevant topics based on the category
    if query_category:
        base_topics = get_topics_for_category(query_category, limit*2)
    else:
        # Mix from all categories
        base_topics = []
        for cat_topics in ALL_CATEGORIES.values():
            base_topics.extend(cat_topics[:5])
        random.shuffle(base_topics)
    
    # Calculate relevance score for each topic compared to the query
    topic_scores = {}
    query_words = set(query.lower().split())
    
    for topic in base_topics:
        score = 0
        topic_words = set(topic.lower().split())
        
        # Score based on word overlap
        common_words = query_words.intersection(topic_words)
        score += len(common_words) * 2
        
        # Bonus for exact match
        if query.lower() in topic.lower() or topic.lower() in query.lower():
            score += 5
            
        topic_scores[topic] = score
    
    # Sort by relevance score
    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Get top topics
    related = [topic for topic, _ in sorted_topics[:limit]]
    
    # If we don't have enough topics, add some generic ones
    if len(related) < limit:
        if "ai" in query.lower() or "intelligence" in query.lower():
            ai_topics = ["Machine Learning", "Neural Networks", "Deep Learning", 
                    "Natural Language Processing", "Computer Vision"]
            for topic in ai_topics:
                if topic not in related:
                    related.append(topic)
                    if len(related) >= limit:
                        break
        elif "blockchain" in query.lower() or "crypto" in query.lower():
            crypto_topics = ["Cryptocurrency", "Bitcoin", "Ethereum", "NFT", "DeFi"]
            for topic in crypto_topics:
                if topic not in related:
                    related.append(topic)
                    if len(related) >= limit:
                        break
    
    return related[:limit]

def update_trending_keywords_from_content(content):
    """Update the agent's trending keywords based on content analysis."""
    topics = extract_trending_topics(content)
    
    from agent.tools import update_keyword_list
    updated = update_keyword_list(topics)
    return updated

if __name__ == "__main__":
    test_content = """
    Artificial intelligence and machine learning are transforming industries across the globe.
    From healthcare to finance, AI systems are automating processes, discovering insights in big data,
    and creating new possibilities. Recent advances in deep learning have accelerated capabilities,
    with neural networks now able to perform complex tasks like image recognition and natural language
    understanding at near-human levels. Meanwhile, blockchain technology continues to disrupt
    traditional financial systems with cryptocurrency applications.
    """
    
    print("Extracted trending topics from content:")
    topics = extract_trending_topics(test_content)
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    
    print("\nRelated topics for 'Artificial Intelligence':")
    related = get_related_topics("Artificial Intelligence")
    for i, topic in enumerate(related, 1):
        print(f"{i}. {topic}")
    
    print("\nCategory detection test:")
    categories = ["technology", "blockchain finance", "mental health wellness", "remote work strategy"]
    for test in categories:
        category = determine_content_category(test)
        print(f"'{test}' => {category or 'No clear category'}") 