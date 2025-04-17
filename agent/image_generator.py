import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import requests

load_dotenv()

class ImageGenerator:
    def __init__(self, api_key=None, output_dir="../api/generated_images"):
        """
        Initialize the ImageGenerator
        
        Args:
            api_key (str, optional): OpenAI API key. If None, will use environment variable.
            output_dir (str): Directory to save generated images
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_image(self, title=None, blog_title=None):
        """
        Generate a blog banner image using DALL-E 3 with a specialized system prompt
        
        Args:
            title (str): The title of the blog post (alternative to blog_title)
            blog_title (str): The title of the blog post (alternative to title)
            
        Returns:
            str: Path to the generated image file, or None if generation failed
        """
        # Use either title or blog_title, preferring title
        final_title = title or blog_title
        if not final_title:
            raise ValueError("Title is required for image generation")
            
        system_prompt = f"""
            Create illustration for my blog on {final_title}. The image should contain text like {final_title}
        """
        
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=system_prompt,
                size="1792x1024",  
                # quality="hd",      
                style="vivid",
                n=1
            )
            image_url = response.data[0].url
            
            image_data = requests.get(image_url).content
            
            filename = f"{self.output_dir}/blog_banner_{final_title.lower().replace(' ', '_')}.png"
            with open(filename, "wb") as f:
                f.write(image_data)
                
            print(f"Blog banner generated successfully and saved as {filename}")
            return image_url
            
        except Exception as e:
            print(f"Error generating blog banner: {str(e)}")
            return None

# def main():
#     generator = ImageGenerator()
#     generator.generate_image("Personal Loan")

# if __name__ == "__main__":
#     main() 