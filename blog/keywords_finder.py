from .trend_api import GoogleTrendsScraper
from .get_topic_v2 import TopicExtractor
import os
import json

class KeywordsFinder:
    def __init__(self):
        self.scraper = GoogleTrendsScraper()
    
    def find_keywords(self, query):        
        self.scraper.fetch_related_topics(query)
        extractor = TopicExtractor("./blog/related_topics.json")
        top_topics = extractor.get_top_topics()
        return top_topics

