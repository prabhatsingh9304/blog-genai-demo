#API
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import sys
import time
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add project root to path to import modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
print(f"Project root added to sys.path: {project_root}")

# Import local modules after adding the project root to sys.path
from agent.base import BlogAgent
from agent.tools import BlogTools
from rag.rag import RAGSystem
from blog.process import Process

load_dotenv()

# Initialize the FastAPI app
app = FastAPI(
    title="Blog Generation API",
    description="API for generating blog posts on various topics using RAG and LLMs",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent and tools
blog_agent = BlogAgent(temperature=0.7, model_name="gpt-3.5-turbo")  # Using a more reliable model by default
blog_tools = BlogTools()

# Define request and response models
class BlogRequest(BaseModel):
    topic: str
    temperature: Optional[float] = 0.7
    model: Optional[str] = "gpt-3.5-turbo"
    save_to_file: Optional[bool] = False
    output_dir: Optional[str] = "generated_blogs"

class BlogResponse(BaseModel):
    topic: str
    content: str
    generated_at: str
    file_path: Optional[str] = None
    generation_time: float

@app.get("/")
async def root():
    return {"message": "Welcome to Blog Generation"}

@app.post("/generate", response_model=BlogResponse)
async def generate_blog(request: BlogRequest):
    """
    Generate a blog post based on the provided topic
    """
    try:
        # Record start time
        start_time = time.time()
        
        # Initialize the agent with requested parameters
        agent = BlogAgent(
            model_name=request.model,
            temperature=request.temperature
        )
        
        # Generate the blog
        topic = agent.User_input(request.topic)
        print(f"Extracted topic: {topic}")
        blog_data = agent.generate_blog(topic, request.topic)
        
        # Calculate generation time
        generation_time = time.time() - start_time
        
        # Save to file if requested
        file_path = None
        if request.save_to_file:
            file_path = blog_tools.save_blog(blog_data, request.output_dir)
        
        # Prepare response
        response = {
            "topic": blog_data["topic"],
            "content": blog_data["content"],
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "file_path": file_path,
            "generation_time": round(generation_time, 2)
        }
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blog generation failed: {str(e)}")

@app.get("/list-blogs")
async def list_blogs(output_dir: Optional[str] = "generated_blogs"):
    """
    List all previously generated blogs
    """
    try:
        blogs = blog_tools.list_generated_blogs(output_dir)
        return {"blogs": blogs, "count": len(blogs)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list blogs: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable is not set.")
        print("Using fallback content generation mode.")
    else:
        # Don't print the actual API key - only that it's available
        print(f"OpenAI API Key detected: {'*' * 8}...{api_key[-4:] if api_key else 'Not Set'}")
        print("Using OpenAI API key for both LLM responses and embeddings.")
    
    # Run the API server with correct module path
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)