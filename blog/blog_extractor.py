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
logger = logging.getLogger('BlogContentExtractor')

class BlogContentExtractor:
    def __init__(self):
        pass
    def fetch_blog_content(self,blogs_urls):  
        #Fetching Link
        try:
            logger.info(f"Found {len(blogs_urls)} URLs to crawl")
            
            # Do crawling and return content
            if blogs_urls:
                # Initialize crawler with the list of URLs 
                crawler = Crawler(blogs_urls)
                # Crawl and get all content as a single string
                content = crawler.process_urls(blogs_urls)
                return content
            else:
                logger.warning("No URLs found to crawl")
                return ""
        except Exception as e:
            logger.error(f"Error in fetch_blog_content: {e}")
            return ""
        
    

        
