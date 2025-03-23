# Blog Generation with RAG

This project demonstrates a blog generation system that uses Retrieval-Augmented Generation (RAG) to create informative blog posts on various topics.

## Features

- Topic-based blog generation using LangChain and OpenAI/OpenRouter
- Support for GPT-4o and other models via OpenRouter
- Trending keyword identification to match user topics with relevant keywords
- RAG implementation for retrieving relevant content from a knowledge base
- Formatted blog output with metadata
- Class-based architecture for better modularity and extensibility

## Project Structure

- `agent/`: Contains the main agent functionality
  - `base.py`: Core `BlogAgent` class for blog generation
  - `tools.py`: `BlogTools` class with utility functions for saving blogs and managing keywords
- `rag/`: Contains RAG implementation
  - `rag.py`: `RAGSystem` class that manages document processing, embedding, and retrieval
- `blog/generated/`: Default output directory for generated blogs
- `example.py`: Example script to demonstrate the system

## Requirements

- Python 3.8+
- OpenAI API key or OpenRouter API key
- Dependencies: langchain, openai, faiss-cpu, python-dotenv

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install langchain openai faiss-cpu python-dotenv
   ```
3. Create a `.env` file in the project root with your API key:
   
   For OpenRouter (recommended for GPT-4o access):
   ```
   OPENROUTER_API_KEY=your-openrouter-api-key-here
   ```
   
   For OpenAI:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

## Using OpenRouter vs OpenAI

This project supports both OpenRouter and OpenAI APIs:

- **OpenRouter**: Provides access to a wide range of models including GPT-4o, Claude, and more. Using OpenRouter is the default.
- **OpenAI**: Direct access to OpenAI models if you have an OpenAI API key.

To use OpenRouter, get an API key from [https://openrouter.ai](https://openrouter.ai) and set it as `OPENROUTER_API_KEY` in your `.env` file.

## Usage

### Command Line Interface

Generate a blog post on a specific topic using GPT-4o via OpenRouter (default):

```bash
python example.py --topic "The future of artificial intelligence in healthcare"
```

Use a different model:

```bash
python example.py --topic "Climate change solutions" --model "anthropic/claude-3-opus"
```

Use OpenAI API directly instead of OpenRouter:

```bash
python example.py --topic "Web development trends" --model "gpt-4" --openai
```

Adjust the temperature for more creative outputs:

```bash
python example.py --topic "Space exploration" --temperature 0.7
```

List available trending keywords:

```bash
python example.py --list-keywords
```

List previously generated blogs:

```bash
python example.py --list-blogs
```

Specify a custom output directory:

```bash
python example.py --topic "Quantum computing" --output-dir "my_blogs"
```

### Using as a Library

You can also use the project as a library in your own code:

```python
from agent.base import BlogAgent
from agent.tools import BlogTools
from rag.rag import RAGSystem

# Initialize components
rag_system = RAGSystem()

# Use GPT-4o via OpenRouter (default)
agent = BlogAgent(model_name="gpt-4o", use_openrouter=True, temperature=0)

# Or use OpenAI directly
# agent = BlogAgent(model_name="gpt-4", use_openrouter=False, temperature=0.3)

tools = BlogTools()

# Generate a blog
blog_data = agent.generate_blog("Quantum computing applications")

# Save the blog
filepath = tools.save_blog(blog_data)
print(f"Blog saved to: {filepath}")
```

## How It Works

1. The system takes a user-provided topic
2. It identifies the most relevant keyword from a list of trending keywords
3. It retrieves relevant content chunks from the RAG system
4. The retrieved content is used to create a context-rich system message
5. The LLM generates a comprehensive blog post using the context and user's topic
6. The generated blog is saved to a file with metadata

## Class Architecture

- **BlogAgent**: Manages the blog generation process, including:
  - Finding relevant keywords
  - Creating system messages with RAG context
  - Generating blog content
  
- **RAGSystem**: Handles the retrieval-augmented generation:
  - Processing and chunking documents
  - Creating and managing embeddings
  - Performing similarity searches
  
- **BlogTools**: Provides utility functions:
  - Saving generated blogs with metadata
  - Managing trending keywords
  - Listing previously generated blogs

## Extending the System

- Add new trending keywords by updating the `trending_keywords` list or using the `add_trending_keywords` method
- Add more crawled content by extending the `DEFAULT_CONTENT` list in the `RAGSystem` class
- Implement web crawling to gather real-time content using the `add_documents` method
- Add blog formatting options or templates for different styles
- Create custom embedding models and pass them to the `RAGSystem` constructor
- Try different models available through OpenRouter