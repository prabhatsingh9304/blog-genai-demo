import os
from dotenv import load_dotenv

def check_api_key(api_key=None):
    """Check if the OpenAI API key is valid and get model availability"""
    if not api_key:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    if not api_key:
        print("ERROR: No API key found in .env file or provided as argument.")
        return False
    
    # Mask API key for security when printing
    masked_key = f"{'*' * 8}...{api_key[-4:]}" if api_key else "Not Set"
    print(f"Checking API key: {masked_key}")
    
    # Check if API key is working by listing models 