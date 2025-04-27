import json
import requests
import os
from dotenv import load_dotenv
from .google_query_search import GoogleQuerySearch

load_dotenv()


class BlogLinkFetcher:
    def __init__(self, num_of_res=10):
        self.num_of_res = num_of_res
    
    def fetch_all_blogs(self, query):
        google_query_search = GoogleQuerySearch(num_of_res=self.num_of_res)
        results = google_query_search.google_search(query)
        return results
    
    def save_results(self, data, output_file):
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Saved blog results to {output_file}")



