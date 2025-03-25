import json

class TopTopics:
    def read_related_queries(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        queries = [
            item["query"]
            for item in data["default"]["rankedList"][0]["rankedKeyword"]
        ]
        return queries[:10]
    

    