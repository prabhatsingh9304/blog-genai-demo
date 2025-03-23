#RAG

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import os
import pickle
import warnings

# Suppress UserWarnings
warnings.filterwarnings("ignore", category=UserWarning)

# **Moved `SafeHuggingFaceEmbeddings` above `RAGSystem`**
class SafeHuggingFaceEmbeddings:
    """Wrapper around HuggingFaceEmbeddings to handle compatibility issues between versions"""
    
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        try:
            # Try different initialization methods
            try:
                # First try with encode_kwargs
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    encode_kwargs={"normalize_embeddings": True}
                )
                setattr(self.embeddings, 'show_progress', False)  # Disable progress bar
            except (TypeError, AttributeError):
                # If that fails, try without extra params
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=model_name
                )
                setattr(self.embeddings, 'show_progress', False)  
        except Exception as e:
            print(f"Error initializing embeddings: {e}")
            # Fall back to a minimal initialization
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            # Manually add a dummy attribute to mimic show_progress
            self.model.show_progress = False
            self.embeddings = self  # Use self as fallback
            
    def embed_documents(self, texts):
        """Embed documents using the underlying model"""
        try:
            return self.embeddings.embed_documents(texts)
        except AttributeError:
            # If the langchain wrapper fails, use sentence_transformers directly
            return [self.model.encode(text) for text in texts]
            
    def embed_query(self, text):
        """Embed a query using the underlying model"""
        try:
            return self.embeddings.embed_query(text)
        except AttributeError:
            # If the langchain wrapper fails, use sentence_transformers directly
            return self.model.encode(text)

# Define RAGSystem class
class RAGSystem:
    """
    Retrieval-Augmented Generation (RAG) system for retrieving relevant content
    based on user queries.
    """
    
    # Sample crawled content (in a real application, this would come from web crawling)
    DEFAULT_CONTENT = [
        """Artificial Intelligence (AI) is transforming industries across the globe. From healthcare 
        to finance, AI systems are automating processes, discovering insights in big data, and 
        creating new possibilities that were once thought impossible. Recent advances in deep learning 
        have particularly accelerated AI capabilities, with neural networks now able to perform complex 
        tasks like image recognition and natural language understanding at near-human levels.""",
        
        """Large Language Models (LLMs) represent one of the most significant breakthroughs in AI 
        in recent years. These models, trained on massive text datasets, can generate human-like text, 
        translate languages, write different kinds of creative content, and answer questions in an 
        informative way. They've enabled applications from chatbots to content generators that are 
        increasingly difficult to distinguish from human-created content.""",
        
        """Retrieval Augmented Generation (RAG) is an approach that combines the strengths of retrieval-based 
        and generation-based methods for natural language processing tasks. It works by first retrieving 
        relevant documents or passages from a knowledge base, then using those retrieved texts to condition 
        a language model to generate more accurate and factual responses. This approach helps ground the model's 
        outputs in verified information, reducing hallucinations and improving factual accuracy.""",
        
        """Machine Learning operations (MLOps) refers to the standardization and streamlining of machine 
        learning lifecycle management. It aims to automate and monitor all steps of ML system construction, 
        including integration, testing, releasing, deployment, and infrastructure management. By implementing 
        MLOps practices, organizations can deliver ML-enabled software with increased speed, while ensuring 
        quality and regulatory compliance.""",
        
        """The ethical implications of AI development are becoming increasingly important as these systems 
        grow more powerful and ubiquitous. Key concerns include bias and fairness in AI systems, transparency 
        and explainability of AI decisions, privacy concerns related to data collection and use, and the 
        potential impacts of automation on employment and economic inequality. Addressing these ethical 
        challenges requires input from diverse stakeholders and the development of robust governance frameworks."""
    ]
    
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
        # Use local embeddings instead of OpenAI
        if embedding_model:
            self.embeddings = embedding_model
        else:
            # Use our safe wrapper
            self.embeddings = SafeHuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        self.db_path = db_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.db = None
        
        # Text splitter for processing documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        if auto_initialize:
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
        if texts is None:
            texts = self.DEFAULT_CONTENT
        
        # Convert texts to Document objects
        documents = [Document(page_content=text) for text in texts]
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Create vector store
        self.db = FAISS.from_documents(chunks, self.embeddings)
        
        # Save the vector store
        self._save_db()
        
        return chunks
    
    def _save_db(self):
        """
        Save the vector database to disk
        """
        with open(self.db_path, "wb") as f:
            pickle.dump(self.db, f)
    
    def load_db(self):
        """
        Load the vector database if it exists, otherwise process documents
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
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
        if self.db is None:
            self.load_db() or self.process_documents()
        
        docs = self.db.similarity_search(query, k=k)
        return docs
    
    def retrieve_relevant_content(self, query, k=3):
        """
        Retrieve relevant content based on the query
        
        Args:
            query (str): The query to search for
            k (int): Number of results to return
            
        Returns:
            str: Formatted content from relevant documents
        """
        # Get similar documents
        relevant_docs = self.similarity_search(query, k=k)
        
        # Format the content for inclusion in the prompt
        formatted_content = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        return formatted_content

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
