# Blog Generation API with OpenAI

This project is a FastAPI-based blog generation system that uses OpenAI's GPT-4 model and embeddings for creating high-quality, relevant blog content.

## Resolving OpenAI API Quota Issues

If you encounter an `insufficient_quota` error or API rate limits, follow these steps:

### 1. Check Your OpenAI Account

1. Go to [OpenAI Platform Billing](https://platform.openai.com/account/billing/overview)
2. Verify you have billing information added and sufficient credits
3. For GPT-4 access, ensure you have a paid plan with access to GPT-4

### 2. Generate a New API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the new key (you won't be able to see it again)

### 3. Update Your API Key

Use the included setup script to update your API key:

```bash
cd /path/to/blog-genai-demo
source venv/bin/activate  # Activate your virtual environment if using one
python setup_api.py --update --key "your-new-api-key-here"
```

Or manually update the `.env` file:

```
OPENAI_API_KEY=your-new-api-key-here
```

## Installation and Setup

1. Clone the repository
2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix/Mac
   # or
   .\venv\Scripts\activate   # Windows
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Setup API key (as described above)
5. Run the server
   ```bash
   python api/main.py
   ```
   or
   ```bash
   uvicorn api.main:app --reload
   ```

## Using the API

### Generate a Blog

```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"topic": "The impact of artificial intelligence in healthcare", "model": "gpt-4"}'
```

### List Generated Blogs

```bash
curl "http://localhost:8000/list-blogs"
```

## API Documentation

Once the server is running, visit:
- API Documentation: http://localhost:8000/docs
- Alternative Documentation: http://localhost:8000/redoc