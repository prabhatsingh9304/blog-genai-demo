# Blog Generation with RAG

This project demonstrates a blog generation system that uses Retrieval-Augmented Generation (RAG) to create informative blog posts on various topics.

## Features

- Topic-based blog generation using LangChain and OpenAI/OpenRouter
- Support for GPT-4o and other models via OpenRouter
- Enhanced RAG implementation for retrieving relevant content based on topic
- Content pattern matching when vector search is unavailable
- Formatted blog output with metadata
- Class-based architecture for better modularity and extensibility

## Project Structure

- `agent/`: Contains the main agent functionality
  - `base.py`: Core `BlogAgent` class for blog generation
  - `tools.py`: `BlogTools` class with utility functions for saving blogs
- `rag/`: Contains RAG implementation
  - `rag.py`: `RAGSystem` class that manages document processing, embedding, and retrieval
- `generated_blogs/`: Default output directory for generated blogs
- `example.py`: Example script to demonstrate the system

## Requirements

- Python 3.8+
- OpenAI API key or OpenRouter API key
- Dependencies: langchain, openai, faiss-cpu, python-dotenv

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install langchain langchain_openai faiss-cpu python-dotenv
   ```
3. Create a `.env` file in the project root with your API key:
   
   For OpenRouter (for LLM calls only):
   ```
   OPENAI_API_KEY=your-openrouter-api-key-here
   ```
   
   For OpenAI (supports both LLM calls and embeddings):
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

## Using OpenRouter vs OpenAI

This project supports both OpenRouter and OpenAI APIs:

- **OpenRouter**: Provides access to a wide range of models including GPT-4o, Claude, and more, but doesn't support embeddings. When using OpenRouter, the RAG system will use fallback content pattern matching.
- **OpenAI**: Direct access to OpenAI models and embeddings if you have an OpenAI API key. This enables full vector search in the RAG system.

To use OpenRouter, get an API key from [https://openrouter.ai](https://openrouter.ai) and set it as `OPENAI_API_KEY` in your `.env` file.

## Usage

### Command Line Interface

Generate a blog post on a specific topic:

```bash
python example.py --topic "The future of artificial intelligence in healthcare"
```

Use a different model:

```bash
python example.py --topic "Climate change solutions" --model "anthropic/claude-3-opus"
```

Adjust the temperature for more creative outputs:

```bash
python example.py --topic "Space exploration" --temperature 0.7
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

# Initialize the agent (automatically initializes RAG)
agent = BlogAgent(model_name="gpt-4o", temperature=0.7)

# Generate a blog
blog_data = agent.generate_blog("Quantum computing applications")

# Initialize tools and save the blog
tools = BlogTools()
filepath = tools.save_blog(blog_data)
print(f"Blog saved to: {filepath}")
```

## How It Works

1. The system takes a user-provided topic
2. It extracts a relevant keyword from the topic
3. It retrieves relevant content chunks from the RAG system:
   - With OpenAI API: Uses embeddings and vector search
   - With OpenRouter API: Uses content pattern matching
4. The retrieved content is used to create a context-rich system message
5. The LLM generates a comprehensive blog post using the context and user's topic
6. The generated blog is saved to a file with metadata

## Class Architecture

- **BlogAgent**: Manages the blog generation process, including:
  - Creating system messages with RAG context
  - Generating blog content
  
- **RAGSystem**: Handles the retrieval-augmented generation:
  - Processing and chunking documents
  - Creating and managing embeddings
  - Vector similarity search or content pattern matching
  
- **BlogTools**: Provides utility functions:
  - Saving generated blogs with metadata
  - Listing previously generated blogs

## Extending the System

- Add more documents to the RAG system by using the `add_documents` method
- Implement web crawling to gather real-time content using the `add_documents` method
- Add blog formatting options or templates for different styles
- Create custom embedding models and pass them to the `RAGSystem` constructor
- Try different models available through OpenRouter

## RAG Implementation Details

The system offers two modes of content retrieval:

1. **Vector Search** (with OpenAI API): 
   - Converts documents into embeddings
   - Uses FAISS for efficient similarity searching
   - Retrieves the most semantically relevant content chunks

2. **Content Pattern Matching** (fallback mode, used with OpenRouter):
   - Recognizes topic categories (finance, technology, etc.)
   - Provides domain-specific structured content 
   - Automatically activates when embeddings are unavailable

This dual approach ensures the system can provide relevant content regardless of API access, while maintaining high-quality outputs.