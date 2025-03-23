# from pytrends.request import TrendReq
# import os
# import sys


# def get_trending_topics(country="united_states", limit=20):
#     """Fetch trending topics from Google Trends for the specified country."""
#     try:
#         pytrend = TrendReq(hl='en-US', tz=360)
#         df = pytrend.trending_searches(pn=country)
#         topics = df[0].tolist()[:limit]
#         return topics
#     except Exception as e:
#         print(f"Error fetching trending topics: {e}")
#         # Return some default topics if Google Trends fails
#         return ["Artificial Intelligence", "Climate Change", "Blockchain", 
#                 "Remote Work", "COVID-19", "Space Exploration"]


# def get_related_topics(query, limit=5):
#     """Get topics related to a specific query from Google Trends."""
#     try:
#         pytrend = TrendReq(hl='en-US', tz=360)
#         pytrend.build_payload(kw_list=[query])
#         related_topics = pytrend.related_topics()
        
#         # Extract rising topics if available
#         if query in related_topics and 'rising' in related_topics[query]:
#             rising_df = related_topics[query]['rising']
#             if not rising_df.empty and 'topic_title' in rising_df.columns:
#                 topics = rising_df['topic_title'].tolist()[:limit]
#                 return topics
        
#         return []
#     except Exception as e:
#         print(f"Error fetching related topics: {e}")
#         return []


# def update_trending_keywords():
#     """Update the agent's trending keywords with topics fetched from Google Trends."""
#     topics = get_trending_topics()
#     # Adjust system path to import update_keyword_list from agent/tools.py
#     sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
#     from agent.tools import update_keyword_list
#     updated = update_keyword_list(topics)
#     return updated


# if __name__ == "__main__":
#     print("Fetching trending topics from Google Trends...")
#     topics = get_trending_topics()
#     print("Trending Topics:")
#     for topic in topics:
#         print(f"- {topic}")
    
#     print("\nUpdating agent's trending keywords...")
#     updated_keywords = update_trending_keywords()
#     print("Updated Trending Keywords:")
#     for keyword in updated_keywords:
#         print(f"- {keyword}")
    
#     # Test related topics
#     test_query = "Artificial Intelligence"
#     print(f"\nFetching topics related to '{test_query}'...")
#     related = get_related_topics(test_query)
#     if related:
#         print(f"Topics related to '{test_query}':")
#         for topic in related:
#             print(f"- {topic}")
#     else:
#         print(f"No related topics found for '{test_query}'")
