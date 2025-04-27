import os
import requests
from dotenv import load_dotenv

load_dotenv()

class GoogleQuerySearch:
    def __init__(self, num_of_res=10):
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API")
        self.google_cx = os.getenv("GOOGLE_CX")
        self.num_of_res = num_of_res
    
    def google_search(self, query):
        search_query = f'"{query}" (intitle:"{query}" OR intext:"{query}") (inurl:blog OR site:medium.com OR site:wordpress.com OR site:blogspot.com OR site:hashnode.com OR site:dev.to) -inurl:/tag/ -inurl:/category/ -inurl:/topics/ -inurl:/labels/ -inurl:/groups/ -inurl:/collections/  -inurl:/blog/  -inurl:/blogs/'
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key, 
            "cx": self.google_cx,
            "q": search_query,
            "num": self.num_of_res
        } 

        response = requests.get(url, params=params)
        if response.status_code == 200:
            res = response.json().get("items",[])
            results = [item.get("link") for item in res]
            print(f"Found {len(results)} results for query: {query}")
            return results
        else:
            print(f"Failed for query: {query} | Status Code: {response.status_code}")
            return []
