#RAG
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import os
import pickle
import warnings
import traceback
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('rag_system')

# Suppress UserWarnings
warnings.filterwarnings("ignore", category=UserWarning)

# Load environment variables
load_dotenv()

# Define RAGSystem class
class RAGSystem:
    """
    Retrieval-Augmented Generation (RAG) system for retrieving relevant content
    based on user queries.
    """
    def __init__(self, 
                 embedding_model="text-embedding-3-small",
                 db_path="vectorstore.pkl",
                 chunk_size=500,
                 chunk_overlap=50,
                 auto_initialize=True):
        """
        Initialize the RAG system.
        
        Args:
            embedding_model: The embedding model to use
            db_path: Path to store/load the vector database
            chunk_size: Size of text chunks for splitting documents
            chunk_overlap: Overlap between chunks
            auto_initialize: Whether to automatically initialize the system
        """
        self.db_path = db_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.db = None
        
        # Initialize OpenAI embeddings if API key is available
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        try:
            self.embeddings = OpenAIEmbeddings(
                model=embedding_model,
                openai_api_key=api_key,
                dimensions=1536,  # For compatibility
                headers={"Content-Type": "application/json"},
                tiktoken_model_name="cl100k_base"  # Explicitly set tokenizer
            )
            
            # Text splitter for processing documents
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            
            if auto_initialize:
                self._initialize_db()
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
            raise
    
    def _initialize_db(self):
        """Initialize the vector database."""
        try:
            logger.info(f"Attempting to load database from {self.db_path}")
            if os.path.exists(self.db_path):
                logger.info(f"Database file exists at {self.db_path}")
                if self.load_db():
                    logger.info("Successfully loaded existing vector database")
                else:
                    logger.info("No existing database found, will initialize on first use")
            else:
                logger.info(f"No database file found at {self.db_path}, will initialize on first use")
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            raise
            
    def add_documents(self, texts):
        """
        Add new documents to the existing database
        
        Args:
            texts: Text document(s) to add (string or list of strings)
            
        Returns:
            list: The processed chunks
        """
        try:
            logger.info("Starting to add documents to RAG system")
            # Handle both single string and list of strings
            if isinstance(texts, str):
                texts = [texts]
                
            if not texts:
                raise ValueError("Empty text provided to add_documents")
                
            # Convert texts to Document objects
            documents = [Document(page_content=text) for text in texts if text.strip()]
            
            if not documents:
                raise ValueError("No valid documents to add")
                
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
            
            if not chunks:
                raise ValueError("No chunks created from documents")
            
            # Create or update vector store
            if self.db is None:
                logger.info("Creating new vector store as none exists")
                self.db = FAISS.from_documents(chunks, self.embeddings)
                logger.info(f"Vector store created with {len(chunks)} chunks")
            else:
                logger.info(f"Adding {len(chunks)} chunks to existing vector store")
                self.db.add_documents(chunks)
            
            # Save the updated vector store
            logger.info("Saving vector store to disk")
            self._save_db()
            logger.info("Successfully saved vector store")
            return chunks
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            if os.getenv("DEBUG", "").lower() == "true":
                traceback.print_exc()
            raise
    
    def _save_db(self):
        """Save the vector database to disk."""
        if self.db is None:
            raise ValueError("No vector store to save")

        try:
            self.db.save_local(folder_path=self.db_path)
            logger.info(f"Vector store saved to {self.db_path}")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            raise

    
    def load_db(self):
        """
        Load the vector database if it exists
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            if os.path.exists(os.path.join(self.db_path, "index.faiss")):
                self.db = FAISS.load_local(folder_path=self.db_path, embeddings=self.embeddings)
                logger.info(f"Loaded vector store from {self.db_path}")
                return True
            else:
                logger.info(f"Vector store folder not found or missing index.faiss: {self.db_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            raise

    
    def similarity_search(self, query, k=3):
        """
        Find similar documents to the query
        
        Args:
            query: The query to search for
            k: Number of results to return
            
        Returns:
            list: List of Document objects similar to the query
        """
        if self.db is None:
            raise ValueError("Vector store not initialized. Please add documents first.")
        
        try:
            docs = self.db.similarity_search(query, k=k)
            logger.info(f"Found {len(docs)} relevant documents for query")
            return docs
        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            raise
    
    def retrieve_relevant_content(self, query, k=3):
        """
        Retrieve relevant content based on the query
        
        Args:
            query: The query to search for
            k: Number of results to return
            
        Returns:
            str: Formatted content from relevant documents
        """
        if not query or query.strip() == "":
            raise ValueError("Empty query provided")
        
        try:
            # Increase k to get more diverse results
            relevant_docs = self.similarity_search(query, k=k*2)
            if not relevant_docs:
                return "No relevant content found for the query."
                
            formatted_content = "\n\n".join([doc.page_content for doc in relevant_docs])
            return formatted_content
        except Exception as e:
            logger.error(f"Error retrieving content: {e}")
            raise

# # Instantiate a global instance for backward compatibility
# _default_rag_system = RAGSystem()

# # For backward compatibility
# def retrieve_relevant_content(query, k=3):
#     """
#     Retrieve relevant content based on the query (wrapper for backward compatibility)
    
#     Args:
#         query: The query to search for
#         k: Number of results to return
        
#     Returns:
#         str: Formatted content from relevant documents
#     """
#     return _default_rag_system.retrieve_relevant_content(query, k=k)

