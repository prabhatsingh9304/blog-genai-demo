import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import agent and tools
from agent.base import BlogAgent
from agent.tools import BlogTools
from rag.rag import RAGSystem

def main():
    """Main function to run the blog generation system"""
    parser = argparse.ArgumentParser(description='Generate a blog post on a given topic')
    parser.add_argument('--topic', type=str, help='Topic for the blog post')
    parser.add_argument('--output-dir', type=str, default='blog/generated', help='Directory to save the generated blog')
    parser.add_argument('--list-keywords', action='store_true', help='List available trending keywords')
    parser.add_argument('--list-blogs', action='store_true', help='List all generated blogs')
    parser.add_argument('--model', type=str, default='gpt-4o', help='OpenAI model to use (default: gpt-4o)')
    parser.add_argument('--temperature', type=float, default=0, help='Temperature for generation (0-1, default: 0)')
    parser.add_argument('--local-trends', action='store_true', help='Use local content analysis for trends instead of external APIs')
    
    args = parser.parse_args()
    
    # Initialize the tools
    tools = BlogTools(default_output_dir=args.output_dir)
    
    # If user wants to list keywords
    if args.list_keywords:
        # Create agent to access keywords
        agent = BlogAgent(model_name=args.model, temperature=args.temperature)
        
        # If local trend analysis is requested, get trends using local content analyzer
        if args.local_trends:
            from blog.content_analyzer import extract_trending_topics
            topics = extract_trending_topics(None, limit=20)
            # Update agent with these topics
            agent.add_trending_keywords(topics)
            print("Available trending keywords (from local analysis):")
        else:
            # Use standard method (which may use external APIs if available)
            print("Real-time trending keywords:")
        
        keywords = agent.get_trending_keywords()
        
        if keywords:
            for i, keyword in enumerate(keywords, 1):
                print(f"{i}. {keyword}")
        else:
            print("No trending keywords available. The system will extract relevant keywords from your topic.")
            
        # Show tip about local trends if not already using them
        if not args.local_trends:
            print("\nTip: Run with --local-trends to analyze content and find related topics")
            
        sys.exit(0)
    
    # List generated blogs if requested
    if args.list_blogs:
        blogs = tools.list_generated_blogs(args.output_dir)
        if not blogs:
            print(f"No blogs found in {args.output_dir}")
            return
            
        print(f"Found {len(blogs)} generated blogs:")
        for i, blog in enumerate(blogs, 1):
            print(f"{i}. {blog['topic']} (Related to: {blog['relevant_keyword']})")
            print(f"   Generated on: {blog['generated_at']}")
            print(f"   File: {blog['filename']}")
            print()
        return
    
    # Check if topic is provided
    if not args.topic:
        parser.print_help()
        return
    
    print(f"Generating blog post on topic: {args.topic}")
    print(f"Using model: {args.model}")
    print(f"Temperature: {args.temperature}")
    print("This might take a minute or two...")
    
    # Initialize the RAG system
    rag_system = RAGSystem()
    
    # Initialize the agent with the RAG system
    agent = BlogAgent(
        model_name=args.model, 
        rag_system=rag_system, 
        temperature=args.temperature
    )
    
    # If using local trends, update agent with local trending topics
    if args.local_trends:
        print("Using local trend analysis...")
        from blog.content_analyzer import extract_trending_topics, get_related_topics
        # Get topics related to the user's query
        topics = get_related_topics(args.topic, limit=10)
        # Update agent with these topics
        agent.add_trending_keywords(topics)
        print(f"Added {len(topics)} local trending topics related to '{args.topic}'")
    
    # Generate the blog
    blog_data = agent.generate_blog(args.topic)
    
    # Save the blog to a file
    filepath = tools.save_blog(blog_data, args.output_dir)
    
    print(f"\nBlog post generated successfully!")
    print(f"Saved to: {filepath}")
    print(f"Related keyword: {blog_data['relevant_keyword']}")

    print(f"Generating comprehensive blog post (1,000+ words) on topic: {args.topic}")
    print(f"Using model: {args.model}")
    print(f"Temperature: {args.temperature}")
    print("This might take a few minutes...")

if __name__ == "__main__":
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable is not set.")
        print("Running in demo mode with limited functionality.")
    elif api_key.startswith("sk-or-v1-"):
        print("Using OpenRouter API key format.")
    else:
        print("Using OpenAI API key format.")
    
    # Continue with main function regardless
    main() 