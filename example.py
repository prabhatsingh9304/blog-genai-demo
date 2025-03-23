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
    parser.add_argument('--model', type=str, default='gpt-4o', help='Model to use (default: gpt-4o)')
    parser.add_argument('--openai', action='store_true', help='Use OpenAI API directly instead of OpenRouter')
    parser.add_argument('--temperature', type=float, default=0, help='Temperature for generation (0-1, default: 0)')
    
    args = parser.parse_args()
    
    # Initialize the tools
    tools = BlogTools(default_output_dir=args.output_dir)
    
    # List trending keywords if requested
    if args.list_keywords:
        # Create agent to access keywords
        agent = BlogAgent(model_name=args.model, temperature=args.temperature)
        keywords = agent.get_trending_keywords()
        print("Available trending keywords:")
        for i, keyword in enumerate(keywords, 1):
            print(f"{i}. {keyword}")
        return
    
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
    
    # Generate the blog
    blog_data = agent.generate_blog(args.topic)
    
    # Save the blog to a file
    filepath = tools.save_blog(blog_data, args.output_dir)
    
    print(f"\nBlog post generated successfully!")
    print(f"Saved to: {filepath}")
    print(f"Related keyword: {blog_data['relevant_keyword']}")

if __name__ == "__main__":
    # Check if API key is set (either OpenRouter or OpenAI)
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: Neither OPENROUTER_API_KEY nor OPENAI_API_KEY environment variable is set.")
        print("Please create a .env file with your API key or set it in your environment.")
        print("Example: OPENROUTER_API_KEY=your-api-key-here")
        print("     or: OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    main() 