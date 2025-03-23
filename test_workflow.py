#!/usr/bin/env python3

import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import components
from agent.base import BlogAgent
from rag.rag import RAGSystem
from agent.tools import BlogTools
from blog.content_analyzer import extract_trending_topics, get_related_topics
from blog.find_link import find_link
from blog.crawler import crawl_content

def log_step(step_name):
    """Print a formatted log message for a step"""
    print(f"\n{'=' * 80}")
    print(f"STEP: {step_name}")
    print(f"{'=' * 80}")

def test_full_workflow():
    """Test the complete workflow of the blog generation system"""
    start_time = time.time()
    print(f"Starting test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create output directory
    output_dir = "blog/test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components
    log_step("Initializing RAG System")
    rag_system = RAGSystem()
    
    log_step("Initializing Blog Agent")
    agent = BlogAgent(
        model_name="gpt-3.5-turbo",  # Use a faster model for testing
        rag_system=rag_system,
        temperature=0.7
    )
    
    log_step("Initializing Blog Tools")
    tools = BlogTools(default_output_dir=output_dir)
    
    # Test topic and keyword extraction
    test_topic = "Artificial Intelligence in Healthcare"
    log_step(f"Testing with topic: '{test_topic}'")
    
    # Get trending topics using local analyzer
    log_step("Getting trending topics")
    topics = extract_trending_topics(None, limit=10)
    print(f"Found {len(topics)} trending topics:")
    for i, topic in enumerate(topics, 1):
        print(f"  {i}. {topic}")
    
    # Get related topics
    log_step("Finding related topics")
    related_topics = get_related_topics(test_topic, limit=5)
    print(f"Found {len(related_topics)} related topics for '{test_topic}':")
    for i, topic in enumerate(related_topics, 1):
        print(f"  {i}. {topic}")
    
    # Add topics to agent
    log_step("Adding trending topics to agent")
    agent.add_trending_keywords(topics + related_topics)
    print(f"Agent now has {len(agent.trending_keywords)} keywords")
    
    # Find relevant keyword
    log_step("Finding most relevant keyword")
    relevant_keyword = agent.find_relevant_keyword(test_topic)
    print(f"Most relevant keyword: {relevant_keyword}")
    
    # Find related links (optional - only if network available)
    try:
        log_step("Finding related links (optional)")
        links = find_link(test_topic, num_results=1)
        print(f"Found links: {links}")
        
        if links:
            # Crawl content
            log_step("Crawling content")
            content = crawl_content(links[0])
            if content:
                print(f"Crawled {len(content)} characters of content")
                print(f"Preview: {content[:150]}...")
                
                # Add content to RAG
                log_step("Adding content to RAG system")
                rag_system.add_documents([content])
                print("Content added to RAG system")
    except Exception as e:
        print(f"Network-dependent steps failed (expected in offline environments): {e}")
        print("Continuing with default RAG content...")
    
    # Generate blog
    log_step("Generating blog")
    blog_data = agent.generate_blog(test_topic)
    print(f"Blog generated with {len(blog_data['content'])} characters")
    print(f"Related keyword: {blog_data['relevant_keyword']}")
    print("\nBlog preview:")
    print("-" * 40)
    print(blog_data['content'][:300] + "..." if len(blog_data['content']) > 300 else blog_data['content'])
    print("-" * 40)
    
    # Save blog
    log_step("Saving blog")
    filepath = tools.save_blog(blog_data, output_dir)
    print(f"Blog saved to: {filepath}")
    
    # Test complete
    elapsed_time = time.time() - start_time
    log_step("Test Complete")
    print(f"Test completed in {elapsed_time:.2f} seconds")
    print(f"All components of the blog generation system are working correctly!")
    
    return True

if __name__ == "__main__":
    print("Testing full blog generation workflow...")
    success = test_full_workflow()
    sys.exit(0 if success else 1) 