#!/usr/bin/env python3
"""
OpenAI API Setup and Verification Script
This script verifies your OpenAI API key and provides information about your subscription.
"""

import os
import requests
import json
import argparse
from dotenv import load_dotenv, set_key

def check_api_key(api_key=None):
    """Check if the OpenAI API key is valid and get model availability"""
    if not api_key:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    if not api_key:
        print("ERROR: No API key found in .env file or provided as argument.")
        return False
    
    # Check if API key is working by listing models
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers
        )
        
        if response.status_code == 200:
            models = response.json()
            print("✅ API key is valid!")
            
            # Check for GPT-4 models
            gpt4_models = [m for m in models.get('data', []) if 'gpt-4' in m.get('id', '')]
            if gpt4_models:
                print("✅ GPT-4 models available:")
                for model in gpt4_models:
                    print(f"  - {model.get('id')}")
            else:
                print("❌ No GPT-4 models available. You may need to join the GPT-4 waitlist or add billing information.")
            
            # Check for embedding models
            embedding_models = [m for m in models.get('data', []) if 'embedding' in m.get('id', '')]
            if embedding_models:
                print("✅ Embedding models available:")
                for model in embedding_models[:3]:  # Show first 3 to avoid overwhelming output
                    print(f"  - {model.get('id')}")
                if len(embedding_models) > 3:
                    print(f"  - ...and {len(embedding_models) - 3} more")
            else:
                print("❌ No embedding models available.")
            
            return True
        
        elif response.status_code == 401:
            print("❌ Invalid API key or unauthorized.")
            print(f"Error details: {response.json().get('error', {}).get('message', 'Unknown error')}")
            return False
        
        elif response.status_code == 429:
            print("❌ Rate limited or exceeded quota.")
            print(f"Error details: {response.json().get('error', {}).get('message', 'Unknown error')}")
            return False
        
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Error details: {response.json().get('error', {}).get('message', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Error connecting to OpenAI API: {e}")
        return False

def update_api_key(new_key):
    """Update the API key in the .env file"""
    try:
        # First make sure the key is valid
        if not check_api_key(new_key):
            print("❌ The provided API key is invalid. Key not updated.")
            return False
        
        # Create .env file if it doesn't exist
        if not os.path.exists('.env'):
            with open('.env', 'w') as f:
                f.write(f"OPENAI_API_KEY={new_key}\n")
            print("✅ Created new .env file with API key.")
        else:
            # Update existing .env file
            set_key('.env', 'OPENAI_API_KEY', new_key)
            print("✅ Updated API key in .env file.")
        
        return True
    
    except Exception as e:
        print(f"❌ Error updating API key: {e}")
        return False

def test_embedding(api_key=None):
    """Test the embedding API"""
    if not api_key:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    if not api_key:
        print("ERROR: No API key found in .env file or provided as argument.")
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "text-embedding-3-small",
        "input": "This is a test."
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Embedding API test successful!")
            print(f"  - Model: {result.get('model')}")
            print(f"  - Embedding dimensions: {len(result.get('data', [{}])[0].get('embedding', []))}")
            return True
        
        elif response.status_code == 429:
            print("❌ Rate limited or exceeded quota for embeddings API.")
            print(f"Error details: {response.json().get('error', {}).get('message', 'Unknown error')}")
            return False
        
        else:
            print(f"❌ Embedding API test failed with status code: {response.status_code}")
            print(f"Error details: {response.json().get('error', {}).get('message', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Error testing embedding API: {e}")
        return False

def refresh_api_key(api_key):
    """Refresh the API key in the .env file with a working key"""
    try:
        # First make sure the key is valid by running a small test
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            print("✅ Test success - API key is valid!")
            # Update the key in .env
            if os.path.exists('.env'):
                set_key('.env', 'OPENAI_API_KEY', api_key)
                print("✅ Updated API key in .env file")
            else:
                with open('.env', 'w') as f:
                    f.write(f"OPENAI_API_KEY={api_key}\n")
                print("✅ Created new .env file with API key")
            return True
        else:
            error_detail = response.json().get('error', {}).get('message', 'Unknown error')
            print(f"❌ API key validation failed: {error_detail}")
            return False
            
    except Exception as e:
        print(f"❌ Error validating or updating API key: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="OpenAI API Setup and Verification")
    parser.add_argument("--key", "-k", help="OpenAI API Key to verify or update")
    parser.add_argument("--update", "-u", action="store_true", help="Update the API key in .env file")
    parser.add_argument("--test-embedding", "-e", action="store_true", help="Test the embedding API")
    parser.add_argument("--refresh", "-r", help="Refresh API key with a new working key")
    
    args = parser.parse_args()
    
    if args.refresh:
        refresh_api_key(args.refresh)
    elif args.update and args.key:
        update_api_key(args.key)
    elif args.test_embedding:
        test_embedding(args.key)
    else:
        print("OpenAI API Key Verification")
        print("==========================")
        check_api_key(args.key)

if __name__ == "__main__":
    main() 