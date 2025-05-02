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
    parser = argparse.ArgumentParser(description='Generate a blog post on a specific topic')
    
    # Add optional arguments
    parser.add_argument('--topic', type=str, help='Topic for the blog post')
    parser.add_argument('--model', type=str, default='gpt-4', help='Model to use (default: gpt-4)')
    parser.add_argument('--list-blogs', action='store_true', help='List existing generated blogs')
    parser.add_argument('--output-dir', '-o', type=str, default='generated_blogs',
                        help='Directory to save generated blogs (default: generated_blogs)')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode with mock responses')
    parser.add_argument('--temperature', type=float, default=0.7, help='Temperature parameter for LLM (default: 0.7)')
    
    args = parser.parse_args()
    
    # Initialize the tools
    tools = BlogTools(default_output_dir=args.output_dir)
    
    # List generated blogs if requested
    if args.list_blogs:
        blogs = tools.list_generated_blogs(args.output_dir)
        if not blogs:
            print(f"No blogs found in {args.output_dir}")
            return
            
        print(f"Found {len(blogs)} generated blogs:")
        for i, blog in enumerate(blogs, 1):
            print(f"{i}. {blog['topic']}")
            if 'relevant_keyword' in blog:
                print(f"   Related to: {blog['relevant_keyword']}")
            print(f"   Generated on: {blog['generated_at']}")
            print(f"   File: {blog['filename']}")
            print()
        return
    
    # Check if topic is provided
    if not args.topic:
        parser.print_help()
        return
    
    print(f"Generating comprehensive blog post on topic: {args.topic}")
    print(f"Using model: {args.model}")
    print(f"Temperature: {args.temperature}")
    print("This might take a few minutes...")
    
    # Initialize the agent
    agent = BlogAgent(
        model_name=args.model, 
        temperature=args.temperature
    )
    
    # Generate the blog
    blog_data = agent.generate_blog(args.topic)
    
    # Save the blog to a file
    filepath = tools.save_blog(blog_data, args.output_dir)
    
    print(f"\nBlog post generated successfully!")
    print(f"Saved to: {filepath}")

if __name__ == "__main__":
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable is not set.")
        print("Running in demo mode with limited functionality.")
    elif api_key.startswith("sk-or-v1-"):
        print("Using OpenRouter API key.")
        print("Note: RAG vector search will use fallback mode as OpenRouter doesn't support embeddings.")
    else:
        print("Using OpenAI API key.")
    
    # Continue with main function
    main() 