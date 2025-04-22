from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document
from langchain_community.llms.fake import FakeListLLM
from langchain_core.messages import HumanMessage, SystemMessage
import os
import sys
import time
import logging
from rag.rag import RAGSystem
from dotenv import load_dotenv
import json
from blog.blog_extractor import BlogContentExtractor
import asyncio
from characters.blog_character import BlogCharacter
from characters.topic_character import TopicCharacter
from characters.keywords_character import KeywordsCharacter
from characters.refine_query_character import RefineQueryCharacter
from blog.keywords_finder import KeywordsFinder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('blog_agent')

# Load environment variables
load_dotenv()

class BlogAgent:
    """
    Agent for generating blog content using LLMs and RAG.
    """
    def __init__(self, model_name="gpt-4-turbo", rag_system=None, temperature=0.7):
        """
        Initialize the blog agent.
        
        Args:
            model_name: LLM model to use
            rag_system: Optional RAG system instance
            temperature: Temperature for LLM responses
        """
        self.model_name = model_name
        self.temperature = temperature
        self.rag_system = rag_system or RAGSystem()
        
        # Initialize LLM
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self._initialize_llm(api_key)
        
    def _initialize_llm(self, api_key):
        """Initialize the LLM with appropriate fallbacks."""
        if not api_key:
            logger.warning("No API key found. Using demo mode with mock responses")
            self._use_mock_llm()
            return
            
        logger.info(f"Using OpenAI API with model: {self.model_name}")
        
        try:
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.temperature,
                openai_api_key=api_key,
                streaming=True,  # Enable streaming
                tiktoken_model_name="cl100k_base"  # Explicitly set tokenizer
            )
            
            # Test the model
            test_result = self.llm.invoke("Write one sentence about AI.")
            logger.info(f"LLM test successful: Model {self.model_name} is working")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error initializing OpenAI ChatModel: {error_msg}")
            
            # Analyze the error and respond appropriately
            if self._is_model_access_error(error_msg):
                self._try_fallback_model(api_key)
            elif self._is_quota_error(error_msg):
                logger.warning("OpenAI API quota exceeded.")
                self._use_mock_llm()
            else:
                logger.warning(f"Unknown error: {error_msg}")
                self._use_mock_llm()
    
    def _is_model_access_error(self, error_msg):
        """Check if error is related to model access."""
        return any(phrase in error_msg for phrase in ["does not exist", "not found", "not available"])
    
    def _is_quota_error(self, error_msg):
        """Check if error is related to quota limits."""
        return any(phrase in error_msg.lower() for phrase in ["quota", "rate limit", "429"])
    
    def _try_fallback_model(self, api_key):
        """Try to use a fallback model."""
        fallback_model = "gpt-3.5-turbo"
        logger.info(f"Model {self.model_name} not found, falling back to {fallback_model}")
        
        try:
            self.llm = ChatOpenAI(
                model_name=fallback_model,
                temperature=self.temperature,
                openai_api_key=api_key
            )
            logger.info(f"Successfully initialized fallback model {fallback_model}")
        except Exception as fallback_error:
            logger.error(f"Could not initialize fallback model: {fallback_error}")
            self._use_mock_llm()
    
    def _use_mock_llm(self):
        """Use a fake LLM for demo mode."""
        logger.info("Using demo mode with mock responses")
        responses = [
            "Artificial Intelligence",
            "This is a sample blog post about the topic. AI has transformed many industries including healthcare, finance, and education.",
            "Machine Learning"
        ]
        self.llm = FakeListLLM(responses=responses)

    def User_input(self, user_input):
        """
        Process user input to extract a blog topic using LLM.
        
        Args:
            user_input: User input string containing blog topic ideas
            
        Returns:
            str: Extracted blog topic from user input
        """
        try:
            prompt = TopicCharacter(user_input).get_character()
            
            topic = self.llm.predict(prompt).strip()
            logger.info(f"Extracted topic from user input: {topic}")
            return topic
        except Exception as e:
            logger.error(f"Error extracting topic from user input: {e}")
            return user_input
    
    def find_relevant_keyword(self, topic, top_related_topics):
        """
        Extract the most relevant keyword from a list of topics.
        
        Args:
            top_related_topics: List of potential topics
            
        Returns:
            str: The most relevant keyword
        """
        if not top_related_topics or len(top_related_topics) == 0:
            logger.warning("No topics provided, using 'general' as fallback")
            return "general"
            
        try:
            # Use LLM to select the most relevant topic
            prompt = KeywordsCharacter(topic, top_related_topics).get_character()
            
            response = self.llm.predict(prompt)
            relevant_topic = response.strip()
            
            # Validate the response
            if relevant_topic not in top_related_topics:
                logger.warning(f"LLM returned '{relevant_topic}' which is not in the provided topics. Using first topic instead.")
                relevant_topic = top_related_topics[0]
                
            logger.info(f"Selected relevant topic: {relevant_topic}")
            return relevant_topic
            
        except Exception as e:
            logger.error(f"Error selecting relevant topic: {e}")
            # Fallback to first topic
            fallback = top_related_topics[0] if top_related_topics else "general"
            logger.info(f"Using fallback topic: {fallback}")
            return fallback

    def create_system_prompt(self, topic, keywords, tone, target_audience, crawled_content):
        """
        Create a system prompt with RAG content for blog generation.
        
        Args:
            topic: The main blog topic
            keywords: The keywords to incorporate
            crawled_content: Optional crawled content to add to RAG
            
        Returns:
            str: A system prompt for the LLM
        """
        start_time = time.time()
        
        # Add crawled content to RAG system
        self.rag_system.add_documents(crawled_content)
        
        # Create an expanded query using the topic and keywords
        expanded_query = f"{topic}"
        
        # Use LLM to refine the search query
        query_refinement_prompt = RefineQueryCharacter(topic).get_character()
        
        try:
            refined_query = self.llm.predict(query_refinement_prompt).strip()
            logger.info(f"Refined search query: {refined_query}")
            
            # Retrieve relevant content using the refined query
            rag_content = self.rag_system.retrieve_relevant_content(refined_query, k=5)
            logger.info(f"Retrieved {len(rag_content.split())} words of relevant content")
            
        except Exception as e:
            logger.error(f"Error in query refinement: {e}")
            # Fallback to original query if refinement fails
            rag_content = self.rag_system.retrieve_relevant_content(expanded_query)
        
        logger.info(f"RAG content: {rag_content}")
        
        logger.info(f"refined query: {refined_query}")
        # Build a more concise prompt
        system_prompt = BlogCharacter(topic, keywords, tone, target_audience, rag_content).get_character()
        
        logger.info(f"System prompt created in {time.time() - start_time:.2f}s")
        return system_prompt
 

    async def generate_blog_stream(self, topic, user_input):
        """
        Generate a blog based on the given topic with streaming support.
        
        Args:
            topic: The topic to generate a blog about
            user_input: Original user input
            
        Yields:
            str: Chunks of the generated blog content
        """
        start_time = time.time()
        logger.info(f"Generating blog on topic: {topic}")
        
        try:
            # Process the topic to find related queries
            blogContentExtractor = BlogContentExtractor(topic)
            top_related_topics = KeywordsFinder().find_keywords(topic)
            logger.info(f"Found {len(top_related_topics)} related topics")
            
            # Find the most relevant keyword
            relevant_keyword = self.find_relevant_keyword(topic, top_related_topics)
            logger.info(f"Selected relevant keyword: {relevant_keyword}")
            
            
            # Fetch blog content using the relevant keyword
            logger.info(f"Fetching content for keyword: {relevant_keyword}")
            crawled_content = blogContentExtractor.fetch_blog_content(relevant_keyword) 
            logger.info(f"Fetched {len(crawled_content) if crawled_content else 0} chars of content")
            # Create system prompt with RAG content
            tone = "Helpful & Value-Driven"
            target_audience = "general"
            system_prompt = self.create_system_prompt(topic, top_related_topics, tone, target_audience, crawled_content)
            
            # Create message objects
            system_message = SystemMessage(content=system_prompt)
            human_message = HumanMessage(content=user_input)
            
            
            # Stream the response
            async for chunk in self.llm.astream([system_message, human_message]):
                if hasattr(chunk, 'content'):
                    yield chunk.content
                elif isinstance(chunk, str):
                    yield chunk
                else:
                    yield str(chunk)
            
            generation_time = time.time() - start_time
            logger.info(f"Blog generated in {generation_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error generating blog: {e}")
            yield f"Error generating blog: {str(e)}"

# Instantiate a default agent for backward compatibility
# default_agent = BlogAgent(temperature=0.7)

# # For backward compatibility - these functions call the default agent's methods
# def find_relevant_keyword(topic):
#     return default_agent.find_relevant_keyword(topic)

# def create_system_message(topic, relevant_keyword=None):
#     return default_agent.create_system_prompt(topic)

# def generate_blog(topic):
#     return default_agent.generate_blog(topic)
 