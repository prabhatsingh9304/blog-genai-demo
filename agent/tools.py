import os
import json
import sys
from datetime import datetime

# Add parent directory to system path (in case this is imported directly)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BlogTools:
    """
    Utility class for working with blog content
    """
    
    def __init__(self, default_output_dir="blog/generated"):
        """
        Initialize BlogTools
        
        Args:
            default_output_dir (str): Default directory to save generated blogs
        """
        self.default_output_dir = default_output_dir
    
    def save_blog(self, blog_data, output_dir=None):
        """
        Save the generated blog to a file
        
        Args:
            blog_data (dict): Dictionary containing blog information
                - topic: The original topic
                - relevant_keyword: The identified relevant keyword
                - content: The generated blog content
            output_dir (str): Directory to save the blog file (uses default if None)
        
        Returns:
            str: Path to the saved file
        """
        if output_dir is None:
            output_dir = self.default_output_dir
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename based on topic and date
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_topic = blog_data["topic"].lower().replace(" ", "_")[:30]
        filename = f"{sanitized_topic}_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Add metadata to the blog content
        blog_content = f"""# {blog_data['topic']}

*Related to: {blog_data['relevant_keyword']}*
*Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

{blog_data['content']}
"""
        
        # Write to file
        with open(filepath, "w") as f:
            f.write(blog_content)
        
        # Save metadata separately
        metadata = {
            "topic": blog_data["topic"],
            "relevant_keyword": blog_data["relevant_keyword"],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": filename
        }
        
        metadata_path = os.path.join(output_dir, f"{sanitized_topic}_{timestamp}_meta.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return filepath
    
    def get_trending_keywords(self, limit=None):
        """
        Get a subset of trending keywords from the agent
        
        Args:
            limit (int): Number of keywords to return
        
        Returns:
            list: List of trending keywords
        """
        from .base import default_agent
        return default_agent.get_trending_keywords(limit)
    
    def update_keyword_list(self, new_keywords):
        """
        Update the trending keywords list in the agent
        
        Args:
            new_keywords (list): New keywords to add to the list
        
        Returns:
            list: Updated list of trending keywords
        """
        from .base import default_agent
        return default_agent.add_trending_keywords(new_keywords)
    
    def list_generated_blogs(self, output_dir=None):
        """
        List all generated blogs
        
        Args:
            output_dir (str): Directory to look for generated blogs (uses default if None)
            
        Returns:
            list: List of dictionaries with blog metadata
        """
        if output_dir is None:
            output_dir = self.default_output_dir
            
        if not os.path.exists(output_dir):
            return []
            
        blogs = []
        
        # Find all metadata files
        for filename in os.listdir(output_dir):
            if filename.endswith("_meta.json"):
                with open(os.path.join(output_dir, filename), "r") as f:
                    metadata = json.load(f)
                    blogs.append(metadata)
        
        # Sort by generation date (newest first)
        blogs.sort(key=lambda x: x["generated_at"], reverse=True)
        
        return blogs

# Create a default tools instance for backward compatibility
default_tools = BlogTools()

# For backward compatibility
def save_blog(blog_data, output_dir="blog/generated"):
    return default_tools.save_blog(blog_data, output_dir)

def get_trending_keywords(limit=10):
    return default_tools.get_trending_keywords(limit)

def update_keyword_list(new_keywords):
    return default_tools.update_keyword_list(new_keywords)

def list_generated_blogs(output_dir=None):
    return default_tools.list_generated_blogs(output_dir)

