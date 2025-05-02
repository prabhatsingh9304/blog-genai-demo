import os
import json
from dotenv import dotenv_values
from serpapi.google_search import GoogleSearch

class GoogleTrendsScraper:
    def __init__(self):
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
        self.env_vars = dotenv_values(env_path)
        self.api_key = self.env_vars.get("SERPAPI_KEY")

        if not self.api_key:
            raise ValueError("❌ SERPAPI_KEY is missing in .env file!")

    def fetch_related_topics(self, query):
        params = {
            "engine": "google_trends",
            "q": query,
            "data_type": "RELATED_TOPICS",
            "api_key": self.api_key
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        related_topics = results.get("related_topics", [])

        # Save results to JSON
        self._save_to_json(related_topics)

        print(f"✅ Saved {len(related_topics)} related topics to related_topics.json")

    def _save_to_json(self, data):
        with open("./blog/related_topics.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    scraper = GoogleTrendsScraper()
    scraper.fetch_related_topics("personal loan")
