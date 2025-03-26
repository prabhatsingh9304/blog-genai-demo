from get_topic import TopTopics
from get_link import BlogLinkFetcher
from get_topic_v2 import GoogleTrendsScraper
from get_topic_v2 import TopicExtractor


class Process:
    def __init__(self, blog_topic):
        self.topic = blog_topic
        
    def fetch_blog_content(self,query):  
        #Fetching Link
        API_KEY = "AIzaSyAyJKQsRoP8esuqeiC3J7OycZvNQ2yolaY"
        CX = "2271740cc80de4f73"
        NumberOfResutsPerTopic = 10

        fetcher = BlogLinkFetcher(api_key=API_KEY, cx=CX, num_of_res=NumberOfResutsPerTopic)
        blogs = fetcher.fetch_all_blogs([query])
        fetcher.save_results(blogs, "link.json")
        
        #do crawling
        
        
    def find_top_queries(self):
        #Import and call trend.py
        #Keep it commented to save api call limit
        # scraper = GoogleTrendsScraper()
        # scraper.fetch_related_topics(self.topic)
        
        #Fetchin top 10 topics
        # queries = TopTopics().read_related_queries("related_topics.json")
        # print("Top Queries:", queries)
        
        extractor = TopicExtractor("related_topics.json")
        top_topics = extractor.get_top_topics()
        return top_topics
        
