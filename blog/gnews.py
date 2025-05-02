import requests
import json
import time

class NewsFetcher:
    def __init__(self, api_key, retries=3, delay=5, output_file="news_data.json"):
        self.api_key = api_key
        self.retries = retries
        self.delay = delay
        self.output_file = output_file

    def fetch_news(self, query):
        url = f"https://gnews.io/api/v4/search?q={query}&country=in&max=2&lang=en&apikey={self.api_key}"

        for attempt in range(self.retries):
            try:
                response = requests.get(url, timeout=10) 
                response.raise_for_status()  

                data = response.json()
                self.save_to_json(data)

                print(f"News data saved successfully in {self.output_file}!")
                return data 
            
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.retries - 1:
                    print(f"Retrying in {self.delay} seconds...")
                    time.sleep(self.delay)
                else:
                    print("Max retries reached. Failed to fetch news.")

        error_data = {"error": "Failed to fetch news", "query": query}
        self.save_to_json(error_data)
        print(f"Saved error message to {self.output_file}.")
        return None

    def save_to_json(self, data):
        with open(self.output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


if __name__ == "__main__":
    api_key = "d943db88eb0a8373c3221a926a3a552a"
    news_fetcher = NewsFetcher(api_key)

    user_query = input("Enter your search query: ")
    news_data = news_fetcher.fetch_news(user_query)

    if news_data:
        print("Fetched news successfully!")
    else:
        print("Failed to fetch news, saved error message.")
