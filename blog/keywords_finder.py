from .trend_api import GoogleTrendsScraper
from .get_topic_v2 import TopicExtractor
import os
class KeywordsFinder:
    def __init__(self):
        self.scraper = GoogleTrendsScraper()
        self.extractor = TopicExtractor("./blog/related_topics.json")
    
    def find_keywords(self, query):        
        self.scraper.fetch_related_topics(query)
        top_topics = self.extractor.get_top_topics()
        return top_topics

