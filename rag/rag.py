#RAG

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import os
import pickle
import warnings

# Suppress UserWarnings
warnings.filterwarnings("ignore", category=UserWarning)

# Define RAGSystem class
class RAGSystem:
    """
    Retrieval-Augmented Generation (RAG) system for retrieving relevant content
    based on user queries.
    """
    
    # Extended comprehensive content for various domains
    DEFAULT_CONTENT = []
    
    def __init__(self, 
                 embedding_model=None,
                 db_path="vectorstore.pkl",
                 chunk_size=500,
                 chunk_overlap=50,
                 auto_initialize=True):
        """
        Initialize the RAG system.
        
        Args:
            embedding_model: The embedding model to use (default: OpenAIEmbeddings)
            db_path (str): Path to store/load the vector database
            chunk_size (int): Size of text chunks for splitting documents
            chunk_overlap (int): Overlap between chunks
            auto_initialize (bool): Whether to automatically initialize the system
        """
        # Get API key
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        # Set default to use fallback unless we confirm a working setup
        self.use_fallback = True
        
        if not api_key:
            print("RAG System: No API key found")
            print("Using fallback content matching instead of vector search")
        else:
            try:
                # Initialize embeddings based on key type
                if embedding_model:
                    self.embeddings = embedding_model
                elif api_key.startswith("sk-or-v1-"):
                    # Using OpenRouter embeddings
                    print("RAG System: Using OpenRouter for embeddings")
                    self.embeddings = OpenAIEmbeddings(
                        model="text-embedding-3-small",
                        openai_api_key=api_key,
                        openai_api_base="https://openrouter.ai/api/v1",
                        headers={"Content-Type": "application/json"}
                    )
                else:
                    # Using OpenAI embeddings
                    print("RAG System: Using OpenAI for embeddings")
                    self.embeddings = OpenAIEmbeddings(
                        model="text-embedding-3-small",
                        openai_api_key=api_key,
                        dimensions=1536,  # Match ada-002 dimensions for backward compatibility
                        headers={"Content-Type": "application/json"}
                    )
                    
                # Test the embeddings to ensure they work
                try:
                    test_result = self.embeddings.embed_query("test embedding")
                    if not test_result or len(test_result) < 10:  # Basic validation
                        print("Warning: Embedding test failed - got invalid response")
                        self.use_fallback = True
                    else:
                        print(f"Embedding test successful - vector dimensions: {len(test_result)}")
                        # If we got here without exception, disable fallback
                        self.use_fallback = False
                except Exception as e:
                    print(f"Warning: Error testing embeddings: {e}")
                    print("Using fallback content matching instead of vector search")
                    self.use_fallback = True
            except Exception as e:
                print(f"Warning: Error initializing embeddings: {e}")
                print("Using fallback content matching instead of vector search")
                
        self.db_path = db_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.db = None
        
        # Text splitter for processing documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        if auto_initialize and not self.use_fallback:
            try:
                self.load_db()
            except:
                self.process_documents()
    
    def add_documents(self, texts):
        """
        Add new documents to the existing database
        
        Args:
            texts (list): List of text documents to add
            
        Returns:
            list: The processed chunks
        """
        # If we're in fallback mode, just return
        if self.use_fallback:
            return []
            
        # Convert texts to Document objects
        documents = [Document(page_content=text) for text in texts]
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        if self.db is None:
            # Create a new vector store if none exists
            self.db = FAISS.from_documents(chunks, self.embeddings)
        else:
            # Add documents to existing store
            self.db.add_documents(chunks)
        
        # Save the updated vector store
        self._save_db()
        
        return chunks
    
    def process_documents(self, texts=None):
        """
        Process documents into chunks and create embeddings
        
        Args:
            texts (list): List of text documents to process. If None, use default content.
            
        Returns:
            list: The processed chunks
        """
        # If we're in fallback mode, just return
        if self.use_fallback:
            return []
            
        if texts is None:
            texts = self.DEFAULT_CONTENT
        
        # Ensure we have at least one document to process
        if not texts:
            print("WARNING: No documents provided for processing. Adding default documents.")
            texts = [
                "This is a default document about personal finance and loans to help initialize the RAG system.",
                "Personal loans are a form of unsecured debt that can be used for various purposes like debt consolidation.",
                "Financial technology has transformed how consumers access credit and banking services.",
                "Artificial intelligence and machine learning are revolutionizing credit scoring and risk assessment."
            ]
        
        # Log document count for debugging
        print(f"Processing {len(texts)} documents for RAG indexing")
        
        # Convert texts to Document objects
        documents = [Document(page_content=text) for text in texts]
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks from {len(texts)} documents")
        
        # Create vector store with error handling
        try:
            # First, check if we can generate embeddings
            test_embedding = self.embeddings.embed_query("test")
            if not test_embedding:
                raise ValueError("Failed to generate embeddings. Check your API key configuration.")
            
            # Create vector store
            print(f"Creating FAISS index with {len(chunks)} chunks")
            self.db = FAISS.from_documents(chunks, self.embeddings)
            print("FAISS index created successfully")
            
            # Save the vector store
            self._save_db()
            print(f"Vector store saved to {self.db_path}")
        except Exception as e:
            print(f"WARNING: Failed to create vector store: {e}")
            print("Falling back to content matching.")
            self.use_fallback = True
            return []
        
        return chunks
    
    def _save_db(self):
        """
        Save the vector database to disk
        """
        if self.use_fallback or self.db is None:
            return
            
        with open(self.db_path, "wb") as f:
            pickle.dump(self.db, f)
    
    def load_db(self):
        """
        Load the vector database if it exists, otherwise process documents
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if self.use_fallback:
            return False
            
        if os.path.exists(self.db_path):
            with open(self.db_path, "rb") as f:
                self.db = pickle.load(f)
            return True
        return False
    
    def similarity_search(self, query, k=3):
        """
        Find similar documents to the query
        
        Args:
            query (str): The query to search for
            k (int): Number of results to return
            
        Returns:
            list: List of Document objects similar to the query
        """
        # If in fallback mode, return empty list
        if self.use_fallback:
            return []
            
        # Try to load or initialize the database
        if self.db is None:
            try:
                if not self.load_db():
                    self.process_documents()
                
                # If still None after loading or processing, go to fallback
                if self.db is None:
                    print("WARNING: Failed to initialize vector store. Falling back to content matching.")
                    self.use_fallback = True
                    return []
            except Exception as e:
                print(f"WARNING: Error initializing database: {e}")
                self.use_fallback = True
                return []
        
        # Perform similarity search with error handling
        try:
            docs = self.db.similarity_search(query, k=k)
            return docs
        except Exception as e:
            print(f"WARNING: Error during similarity search: {e}")
            self.use_fallback = True
            return []
    
    def retrieve_relevant_content(self, query, k=3):
        """
        Retrieve relevant content based on the query
        
        Args:
            query (str): The query to search for
            k (int): Number of results to return
            
        Returns:
            str: Formatted content from relevant documents
        """
        # If in fallback mode, provide better fallback content
        if self.use_fallback:
            print("NOTICE: Using fallback content mode instead of vector search.")
            
            # Create a more helpful fallback response for personal loans if that's the topic
            if "loan" in query.lower() or "personal loan" in query.lower() or "finance" in query.lower():
                return """
                When writing about personal loans, consider including:
                
                # Key Trends in Personal Loans
                
                ## Digital Transformation
                - Online application processes and instant approvals
                - Mobile apps for loan management and repayment
                - AI-powered credit scoring models beyond traditional FICO scores
                
                ## Fintech Revolution
                - Peer-to-peer lending platforms connecting borrowers directly to investors
                - Buy Now Pay Later (BNPL) services as alternatives to traditional loans
                - Blockchain and cryptocurrency-backed loans
                
                ## Personalization
                - Risk-based pricing models tailored to individual profiles
                - Flexible repayment schedules and options
                - Specialized loan products for specific needs (debt consolidation, home improvement)
                
                ## Regulatory Environment
                - Open banking initiatives improving access to financial data
                - Consumer protection regulations affecting loan terms
                - Responsible lending practices and transparency requirements
                
                ## Economic Factors
                - Interest rate trends and Federal Reserve policies
                - Inflation's impact on borrowing and repayment
                - Post-pandemic recovery effects on loan availability
                """
            
            # Simple keyword matching as fallback for other topics
            try:
                from blog.content_analyzer import get_related_content
                fallback_content = get_related_content(query)
                if fallback_content:
                    return fallback_content
            except Exception:
                pass
                
            # If content analyzer also fails, return minimal content
            return f"""
            When writing about {query}, consider including:
            - Introduction explaining key concepts and relevance
            - Current trends and innovations in the field
            - Benefits and advantages for users/consumers
            - Challenges and potential solutions
            - Real-world applications and case studies
            - Best practices and recommendations
            - Future outlook and predictions
            """
        
        try:
            # Use vector search with embeddings API
            relevant_docs = self.similarity_search(query, k=k)
            
            # If we've switched to fallback mode during similarity search
            if self.use_fallback or not relevant_docs:
                # Recursively call this method now that we're in fallback mode
                return self.retrieve_relevant_content(query, k=k)
                
            formatted_content = "\n\n".join([doc.page_content for doc in relevant_docs])
            return formatted_content
        except Exception as e:
            # Switch to fallback mode and try again
            print(f"WARNING: Error during vector search: {e}. Switching to fallback mode.")
            self.use_fallback = True
            return self.retrieve_relevant_content(query, k=k)

# Instantiate a global instance for backward compatibility
_default_rag_system = RAGSystem()

# For backward compatibility
def retrieve_relevant_content(query, k=3):
    """
    Retrieve relevant content based on the query (wrapper for backward compatibility)
    
    Args:
        query (str): The query to search for
        k (int): Number of results to return
        
    Returns:
        str: Formatted content from relevant documents
    """
    return _default_rag_system.retrieve_relevant_content(query, k=k) 