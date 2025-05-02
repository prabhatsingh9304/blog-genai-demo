#RAG
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SKLearnVectorStore
from langchain.docstore.document import Document
import os
import pickle
import warnings
import traceback
import logging
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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
                 db_path="sklearn_vectorstore.parquet",
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
        self.db_path = os.path.join(os.getcwd(), db_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.db = None
        self.vectorstore = None
        
        # Initialize OpenAI embeddings if API key is available
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        try:
            self.embeddings = OpenAIEmbeddings(
                model=embedding_model,
                openai_api_key=api_key
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
                self.vectorstore = SKLearnVectorStore.load_local(
                    folder_path=os.path.dirname(self.db_path),
                    embeddings=self.embeddings
                )
                logger.info("Successfully loaded existing vector database")
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
            
            # Create or update vectorstore
            if self.vectorstore is None:
                self.vectorstore = SKLearnVectorStore.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_path=self.db_path,
                    serializer="parquet"
                )
            else:
                self.vectorstore.add_documents(chunks)
            
            # Save the updated database
            logger.info("Saving database to disk")
            self.vectorstore.persist()
            logger.info("Successfully saved database")
            return chunks
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            if os.getenv("DEBUG", "").lower() == "true":
                traceback.print_exc()
            raise
    
    def retrieve_relevant_content(self, query, k=3):
        """
        
        Args:
            query: The query to search for
            k: Number of results to return
            
        Returns:
            str: Formatted content from relevant documents
        """
        if not query or query.strip() == "":
            raise ValueError("Empty query provided")
        
        if self.embeddings_matrix is None or len(self.documents) == 0:
            return "No documents in the database."
        
        try:
            # Get query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Calculate cosine similarity
            similarities = cosine_similarity([query_embedding], self.embeddings_matrix)[0]
            
            # Get top k indices
            top_k_indices = np.argsort(similarities)[-k:][::-1]
            
            # Get corresponding documents
            relevant_docs = [self.documents[i] for i in top_k_indices]
            
            if not relevant_docs:
                return "No relevant content found for the query."
                
            formatted_content = "\n\n".join([doc.page_content for doc in relevant_docs])
            return formatted_content
        except Exception as e:
            logger.error(f"Error retrieving content: {e}")
            raise


