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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('rag_system')

# Suppress UserWarnings
warnings.filterwarnings("ignore", category=UserWarning)

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
        self.use_fallback = True
        
        # Initialize OpenAI embeddings if API key is available
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if self._setup_embeddings(api_key, embedding_model):
            # Text splitter for processing documents
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            
            if auto_initialize and not self.use_fallback:
                self._initialize_db()
    
    def _setup_embeddings(self, api_key, embedding_model):
        """Set up the embeddings model."""
        if not api_key:
            logger.warning("No API key found, using fallback content matching")
            return False
            
        try:
            logger.info("Using OpenAI for embeddings")
            self.embeddings = OpenAIEmbeddings(
                model=embedding_model,
                openai_api_key=api_key,
                dimensions=1536,  # For compatibility
                headers={"Content-Type": "application/json"}
            )
            self.use_fallback = False
            return True
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            logger.info("Using fallback content matching")
            return False
    
    def _initialize_db(self):
        """Initialize the vector database."""
        try:
            if self.load_db():
                logger.info("Successfully loaded existing vector database")
            else:
                logger.info("No existing database found, will initialize on first use")
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            
    def add_documents(self, texts):
        """
        Add new documents to the existing database
        
        Args:
            texts: Text document(s) to add (string or list of strings)
            
        Returns:
            list: The processed chunks
        """
        if self.use_fallback:
            logger.info("In fallback mode, not adding documents to vector store")
            return []
            
        try:
            # Handle both single string and list of strings
            if isinstance(texts, str):
                texts = [texts]
                
            if not texts:
                logger.warning("Empty text provided to add_documents")
                return []
                
            # Convert texts to Document objects
            documents = [Document(page_content=text) for text in texts if text.strip()]
            
            if not documents:
                logger.warning("No valid documents to add")
                return []
                
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
            
            if not chunks:
                logger.warning("No chunks created from documents")
                return []
            
            # Create or update vector store
            if self.db is None:
                logger.info("Creating new vector store")
                self.db = FAISS.from_documents(chunks, self.embeddings)
                logger.info(f"Vector store created with {len(chunks)} chunks")
            else:
                logger.info(f"Adding {len(chunks)} chunks to existing vector store")
                self.db.add_documents(chunks)
            
            # Save the updated vector store
            self._save_db()
            return chunks
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            if os.getenv("DEBUG", "").lower() == "true":
                traceback.print_exc()
            return []
    
    def _save_db(self):
        """Save the vector database to disk."""
        if self.use_fallback or self.db is None:
            return
            
        try:
            with open(self.db_path, "wb") as f:
                pickle.dump(self.db, f)
            logger.info(f"Vector store saved to {self.db_path}")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
    
    def load_db(self):
        """
        Load the vector database if it exists
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if self.use_fallback:
            return False
            
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "rb") as f:
                    if os.path.getsize(self.db_path) > 0:  # Check if file isn't empty
                        self.db = pickle.load(f)
                        logger.info(f"Loaded vector store from {self.db_path}")
                        return True
                    else:
                        logger.warning(f"Vector store file exists but is empty: {self.db_path}")
                        return False
            except (EOFError, pickle.UnpicklingError) as e:
                logger.error(f"Error loading vector store (file may be corrupted): {e}")
                # If file is corrupted, rename it and create a new one
                try:
                    backup_path = f"{self.db_path}.backup"
                    logger.info(f"Backing up corrupted file to {backup_path}")
                    os.rename(self.db_path, backup_path)
                except Exception as rename_error:
                    logger.error(f"Failed to backup corrupted file: {rename_error}")
                return False
            except Exception as e:
                logger.error(f"Error loading vector store: {e}")
                return False
        else:
            logger.info(f"Vector store file not found: {self.db_path}")
        return False
    
    def similarity_search(self, query, k=3):
        """
        Find similar documents to the query
        
        Args:
            query: The query to search for
            k: Number of results to return
            
        Returns:
            list: List of Document objects similar to the query
        """
        if self.use_fallback:
            return []
            
        # Try to load or initialize the database
        if self.db is None:
            try:
                if not self.load_db():
                    logger.warning("No vector store found and no documents provided yet")
                    self.use_fallback = True
                    return []
            except Exception as e:
                logger.error(f"Error initializing database: {e}")
                self.use_fallback = True
                return []
        
        # Perform similarity search
        try:
            docs = self.db.similarity_search(query, k=k)
            logger.info(f"Found {len(docs)} relevant documents for query")
            return docs
        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            self.use_fallback = True
            return []
    
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
            logger.warning("Empty query provided")
            return "No specific query provided. Please provide a detailed topic."
        
        # If in fallback mode, provide fallback content
        if self.use_fallback:
            logger.info(f"Using content pattern matching for query: '{query}'")
            return self._get_fallback_content(query)
        
        try:
            relevant_docs = self.similarity_search(query, k=k)
            
            # If we've switched to fallback mode during search
            if self.use_fallback or not relevant_docs:
                logger.info("Falling back to pattern matching")
                return self._get_fallback_content(query)
                
            formatted_content = "\n\n".join([doc.page_content for doc in relevant_docs])
            return formatted_content
        except Exception as e:
            logger.error(f"Error retrieving content: {e}")
            self.use_fallback = True
            return self._get_fallback_content(query)
    
    def _get_fallback_content(self, query):
        """Generate fallback content based on the query."""
        # Finance/loan topics
        if any(term in query.lower() for term in ["loan", "finance", "banking", "credit", "mortgage"]):
            return self._get_finance_fallback()
            
        # Technology topics
        elif any(term in query.lower() for term in ["tech", "ai", "software", "digital", "app", "internet", "web"]):
            return self._get_technology_fallback()
            
        # Generic structure for other topics
        return self._get_generic_fallback(query)
    
    def _get_finance_fallback(self):
        """Get finance-related fallback content."""
        return """
        # Key Trends in Personal Finance & Loans
        
        ## Digital Transformation
        - Online application processes and instant approvals
        - Mobile apps for loan management and repayment
        - AI-powered credit scoring models beyond traditional FICO scores
        
        ## Fintech Innovation
        - Peer-to-peer lending platforms connecting borrowers directly to investors
        - Buy Now Pay Later (BNPL) services as alternatives to traditional loans
        - Blockchain and cryptocurrency-backed loans
        - Digital banks offering competitive rates and streamlined experiences
        
        ## Personalization & Flexibility
        - Risk-based pricing models tailored to individual profiles
        - Flexible repayment schedules and options
        - Specialized loan products for specific needs (debt consolidation, home improvement)
        - Early payoff options with reduced or no penalties
        
        ## Regulatory Environment
        - Open banking initiatives improving access to financial data
        - Consumer protection regulations affecting loan terms
        - Responsible lending practices and transparency requirements
        - Impact of interest rate policies on loan availability and terms
        
        ## Economic Factors
        - Interest rate trends and Federal Reserve policies
        - Inflation's impact on borrowing and repayment
        - Post-pandemic recovery effects on loan availability
        - Housing market trends affecting mortgage and home equity loans
        """
    
    def _get_technology_fallback(self):
        """Get technology-related fallback content."""
        return """
        # Key Elements for Technology Content
        
        ## Current Industry Trends
        - AI and machine learning integration across sectors
        - Edge computing and distributed infrastructure
        - Digital transformation acceleration post-pandemic
        - Cybersecurity in an increasingly vulnerable landscape
        
        ## Technological Innovation
        - Advances in natural language processing and computer vision
        - Quantum computing developments and practical applications
        - Internet of Things (IoT) ecosystem expansion
        - Blockchain beyond cryptocurrency: supply chain, healthcare, legal
        
        ## User Experience & Design
        - Human-centered design principles
        - Accessibility and inclusive design practices
        - Voice and multimodal interfaces
        - Personalization through data-driven insights
        
        ## Business Impact
        - Subscription-based models and recurring revenue
        - Cloud migration and infrastructure modernization
        - Remote work technologies and distributed teams
        - Data privacy regulations and compliance challenges
        
        ## Future Outlook
        - Emerging technologies to watch
        - Sustainability and green tech initiatives
        - Digital ethics and responsible innovation
        - Skills and workforce transformation
        """
    
    def _get_generic_fallback(self, query):
        """Get generic fallback content for any topic."""
        return f"""
        # Content Structure for "{query}"
        
        ## Introduction
        - Core concepts and definitions
        - Historical context and evolution
        - Current relevance and importance
        - Main challenges and opportunities
        
        ## Key Developments
        - Recent innovations and breakthroughs
        - Statistical trends and data points
        - Industry standards and best practices
        - Comparative analysis of different approaches
        
        ## Practical Applications
        - Real-world use cases and examples
        - Implementation strategies
        - Benefits and limitations
        - Cost-benefit considerations
        
        ## Future Outlook
        - Emerging trends and predictions
        - Potential challenges and solutions
        - Research directions and opportunities
        - Long-term impact and significance
        
        ## Recommendations
        - Strategic advice for stakeholders
        - Action steps for implementation
        - Resources for further learning
        - Evaluation metrics for success
        """

# Instantiate a global instance for backward compatibility
_default_rag_system = RAGSystem()

# For backward compatibility
def retrieve_relevant_content(query, k=3):
    """
    Retrieve relevant content based on the query (wrapper for backward compatibility)
    
    Args:
        query: The query to search for
        k: Number of results to return
        
    Returns:
        str: Formatted content from relevant documents
    """
    return _default_rag_system.retrieve_relevant_content(query, k=k)

