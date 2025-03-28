from .get_topic import TopTopics
from .get_link import BlogLinkFetcher
from .get_topic_v2 import TopicExtractor
from .crawler import Crawler
from .trend_api import GoogleTrendsScraper
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('process')

class Process:
    def __init__(self, blog_topic):
        self.topic = blog_topic
        
    def fetch_blog_content(self,query):  
        #Fetching Link
        google_api_key = os.getenv("GOOGLE_SEARCH_API")
        google_cx = os.getenv("GOOGLE_CX")
        NumberOfResutsPerTopic = 10

        try:
            fetcher = BlogLinkFetcher(api_key=google_api_key, cx=google_cx, num_of_res=NumberOfResutsPerTopic)
            blogs = fetcher.fetch_all_blogs(query)
            fetcher.save_results(blogs, "./blog/link.json")
            
        
            # Get the URLs from the fetched blogs
            urls = []
            for url in blogs:
                urls.append(url)
                
            logger.info(f"Found {len(urls)} URLs to crawl")
            
            # Do crawling and return content
            if urls:
                # Initialize crawler with the list of URLs
                crawler = Crawler(urls)
                # Crawl and get all content as a single string
                content = crawler.process_urls(urls)
                return content
            else:
                logger.warning("No URLs found to crawl")
                return ""
        except Exception as e:
            logger.error(f"Error in fetch_blog_content: {e}")
            return ""
        
    def find_top_queries(self):
        
            #Import and call trend.py
            #Keep it commented to save api call limit
        scraper = GoogleTrendsScraper()
        scraper.fetch_related_topics(self.topic)
        
        extractor = TopicExtractor("./blog/related_topics.json")
        top_topics = extractor.get_top_topics()
        return top_topics
    

        
