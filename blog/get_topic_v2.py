import json

class TopicExtractor:
    def __init__(self, json_file):
        self.json_file = json_file
        self.data = self._load_json()

    def _load_json(self):
        with open(self.json_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_top_topics(self, limit=10):
        topics = []
        for item in self.data.get("top", []):
            topics.append(item["topic"]["title"])
            
        if not topics:
            raise ValueError("No topics found in the data")
            
        return topics[:min(limit, len(topics))]

# Example usage:
# extractor = TrendExtractor("related_topics.json")
# top_topics = extractor.get_top_topics()
# print(top_topics)
