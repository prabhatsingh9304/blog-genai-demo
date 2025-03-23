from googlesearch import search
import requests
import time


def find_link(query, num_results=3, max_retries=3):
    """
    Search for relevant links using Google Search.
    Returns a list of valid links that can be accessed.
    """
    search_query = f"{query} blog article"
    results = []
    retries = 0
    
    while retries < max_retries and len(results) < num_results:
        try:
            # Use Google Search to find links
            found_urls = list(search(search_query, num=num_results*2, stop=num_results*2))
            
            # Validate each URL (check if accessible)
            for url in found_urls:
                if url in results:
                    continue
                    
                try:
                    # Check if the URL is accessible
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        results.append(url)
                        if len(results) >= num_results:
                            break
                except requests.RequestException:
                    # Skip URLs that can't be accessed
                    continue
                    
            # If we found enough links or no links were found, break
            if len(results) >= num_results or not found_urls:
                break
                
            retries += 1
            time.sleep(1)  # Avoid hitting rate limits
            
        except Exception as e:
            print(f"Error searching for links: {e}")
            retries += 1
            time.sleep(2)  # Wait longer if there's an error
    
    return results


def get_best_link_for_topic(topic):
    """Get the best link for a specific topic."""
    links = find_link(topic, num_results=1)
    if links:
        return links[0]
    return None


if __name__ == "__main__":
    query = input("Enter the topic to search for links: ")
    links = find_link(query)
    print(f"Found {len(links)} relevant links:")
    for i, link in enumerate(links, 1):
        print(f"{i}. {link}")
