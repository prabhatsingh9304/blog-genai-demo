#crawl links
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time


def clean_text(text):
    """Clean and normalize extracted text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove very short lines (likely navigation elements)
    lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 40]
    return '\n'.join(lines)


def extract_article_content(soup):
    """
    Try to extract the main article content using common patterns.
    Returns the extracted text or None if no content was found.
    """
    # Look for article tag
    article = soup.find('article')
    if article:
        return clean_text(article.get_text())
    
    # Look for main tag
    main = soup.find('main')
    if main:
        return clean_text(main.get_text())
    
    # Look for common content div classes/ids
    for selector in ['.post-content', '.entry-content', '.article-content', '#content', '.content']:
        content = soup.select_one(selector)
        if content:
            return clean_text(content.get_text())
    
    # If no structured content found, try to extract paragraphs
    paragraphs = soup.find_all('p')
    if paragraphs:
        # Only keep paragraphs with reasonable length (to filter out navigation, etc.)
        meaningful_paragraphs = [p.get_text() for p in paragraphs if len(p.get_text()) > 50]
        if meaningful_paragraphs:
            return clean_text('\n'.join(meaningful_paragraphs))
    
    return None


def crawl_content(url, timeout=15):
    """
    Crawl the given URL and extract textual content from the page.
    Returns cleaned and structured content or None if failed.
    """
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        return None
    
    try:
        # Add user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    
    # Check content type
    content_type = response.headers.get('Content-Type', '')
    if 'text/html' not in content_type:
        print(f"Skipping non-HTML content: {content_type}")
        return None
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove script, style, nav, header, footer elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        element.decompose()
    
    # Try to extract article content
    article_content = extract_article_content(soup)
    if article_content:
        return article_content
    
    # Fallback to extracting all visible text
    texts = soup.stripped_strings
    return clean_text('\n'.join(texts))


def crawl_multiple_links(urls):
    """
    Crawl multiple URLs and return a dictionary mapping URLs to their content.
    Only returns entries for successfully crawled URLs.
    """
    results = {}
    for url in urls:
        print(f"Crawling: {url}")
        content = crawl_content(url)
        if content:
            # Get the domain for logging
            domain = urlparse(url).netloc
            print(f"Successfully crawled {domain} ({len(content)} chars)")
            results[url] = content
        time.sleep(1)  # Be nice to the servers
    
    return results


if __name__ == '__main__':
    url = input("Enter a URL to crawl: ")
    content = crawl_content(url)
    if content:
        print("\nExtracted Content:")
        print("-" * 80)
        print(content)
        print("-" * 80)
        print(f"Total content length: {len(content)} characters")
    else:
        print("Failed to extract content.")
