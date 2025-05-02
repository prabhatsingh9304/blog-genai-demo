# Web content crawler
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('crawler')

class Crawler:
    """Web content crawler that extracts text from web pages."""
    
    def __init__(self, urls=None):
        """
        Initialize the crawler with a list of URLs.
        
        Args:
            urls (list): List of URLs to crawl (optional)
        """
        self.urls = urls or []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def clean_text(self, text):
        """
        Clean and normalize extracted text.
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove very short lines (likely navigation elements)
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 40]
        
        return '\n'.join(lines)

    def extract_article_content(self, soup):
        """
        Extract the main article content using common patterns.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            str: Extracted text or None if no content was found
        """
        # Strategy 1: Look for article tag
        article = soup.find('article')
        if article:
            return self.clean_text(article.get_text())
        
        # Strategy 2: Look for main tag
        main = soup.find('main')
        if main:
            return self.clean_text(main.get_text())
        
        # Strategy 3: Look for common content div classes/ids
        content_selectors = [
            '.post-content', '.entry-content', '.article-content', 
            '#content', '.content', '.post', '.entry', '.blog-post'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                return self.clean_text(content.get_text())
        
        # Strategy 4: Extract meaningful paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            meaningful_paragraphs = [p.get_text() for p in paragraphs if len(p.get_text()) > 50]
            if meaningful_paragraphs:
                return self.clean_text('\n'.join(meaningful_paragraphs))
        
        return None

    def crawl_content(self, url, timeout=15):
        """
        Crawl a URL and extract textual content.
        
        Args:
            url (str): URL to crawl
            timeout (int): Request timeout in seconds
            
        Returns:
            str: Cleaned content or None if failed
        """
        # Validate URL
        if not url or not url.startswith(('http://', 'https://')):
            logger.warning(f"Invalid URL: {url}")
            return None
        
        try:
            # Fetch the page
            logger.info(f"Fetching URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                logger.info(f"Skipping non-HTML content: {content_type}")
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove non-content elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                element.decompose()
            
            # Extract content
            article_content = self.extract_article_content(soup)
            
            if article_content:
                domain = urlparse(url).netloc
                logger.info(f"Extracted {len(article_content)} chars from {domain}")
                return article_content
            
            # Fallback to all text
            logger.info("No structured content found, extracting all text")
            texts = list(soup.stripped_strings)
            return self.clean_text('\n'.join(texts))
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url}")
            return None
            
        except requests.exceptions.TooManyRedirects:
            logger.error(f"Too many redirects for {url}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error processing {url}: {e}")
            return None

    def process_urls(self, urls=None):
        """
        Process multiple URLs and concatenate their content.
        
        Args:
            urls (list): URLs to process (uses self.urls if None)
            
        Returns:
            str: Concatenated content from all URLs
        """
        urls_to_process = urls or self.urls
        
        if not urls_to_process:
            logger.warning("No URLs provided for processing")
            return ""
        
        logger.info(f"Processing {len(urls_to_process)} URLs")
        
        all_content = []
        successful_crawls = 0
        
        for url in urls_to_process:
            try:
                content = self.crawl_content(url)
                
                if content:
                    domain = urlparse(url).netloc
                    content_length = len(content)
                    logger.info(f"Successfully crawled {domain} ({content_length} chars)")
                    
                    # Add domain as context before the content
                    formatted_content = f"Source: {domain}\n\n{content}"
                    all_content.append(formatted_content)
                    successful_crawls += 1
                else:
                    logger.warning(f"No content extracted from {url}")
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
            
            # Be nice to servers
            time.sleep(1)
        
        # Join all content with separators
        final_content = "\n\n" + "-" * 40 + "\n\n".join(all_content) if all_content else ""
        
        logger.info(f"Total content: {len(final_content)} chars from {successful_crawls}/{len(urls_to_process)} URLs")
        return final_content

    # if __name__ == '__main__':
    #     url = input("Enter a URL to crawl: ")
    #     content = crawl_content(url)
    #     if content:
    #         print("\nExtracted Content:")
    #         print("-" * 80)
    #         print(content)
    #         print("-" * 80)
    #         print(f"Total content length: {len(content)} characters")
    #     else:
    #         print("Failed to extract content.")
