import json
import requests


class BlogLinkFetcher:
    def __init__(self, api_key, cx, num_of_res):
        self.api_key = api_key
        self.cx = cx
        self.num = num_of_res
    
    def search_blogs(self, query):
        search_query = f'"{query}" (intitle:"{query}" OR intext:"{query}") (inurl:blog OR site:medium.com OR site:wordpress.com OR site:blogspot.com OR site:hashnode.com OR site:dev.to) -inurl:/tag/ -inurl:/category/ -inurl:/topics/ -inurl:/labels/ -inurl:/groups/ -inurl:/collections/  -inurl:/blog/  -inurl:/blogs/'

        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": search_query,
            "num": self.num
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

    def fetch_all_blogs(self, queries):
        blogs = {}
        for query in queries:
            results = self.search_blogs(query)
            blogs[query] = results 
        return blogs
    
    def save_results(self, data, output_file):
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Saved blog results to {output_file}")



