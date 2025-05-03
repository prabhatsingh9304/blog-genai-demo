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
from characters.keywords_list_character import KeywordListCharacter
from characters.refine_query_character import RefineQueryCharacter
from blog.keywords_finder import KeywordsFinder
from agent.agent_memory import AgentMemory
from blog.get_link import BlogLinkFetcher
from characters.parse_request_character import ParseRequestCharacter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('blog_agent')

# Load environment variables
load_dotenv()

class BlogAgent:
    """
    Agent for generating blog content using LLMs and RAG.
    """
    def __init__(self, model_name="gpt-4-turbo", rag_system=None, temperature=0.7, session_id=None):
        """
        Initialize the blog agent.
        
        Args:
            model_name: LLM model to use
            rag_system: Optional RAG system instance
            temperature: Temperature for LLM responses
            session_id: Optional session ID for memory persistence
        """
        self.model_name = model_name
        self.temperature = temperature
        self.rag_system = rag_system or RAGSystem()
        
        # Initialize memory
        self.memory = AgentMemory(session_id=session_id)
        
        # Initialize LLM
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self._initialize_llm(api_key)
        
    def _initialize_llm(self, api_key):
        """Initialize the LLM."""
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
            logger.warning("Using demo mode with mock responses due to error")
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

    def parse_request(self, request):
        """
        Process a blog generation request and determine whether the user wants to
        generate a new blog or improve an existing one.
        
        Args:
            request: String containing the user's request
            
        Returns:
            dict: A command object with 'action' being either 'generate' or 'improve'
                  and other relevant parameters
        """
        logger.info(f"Processing user request: {request}")
        
        # Store request in memory
        self.memory.add_user_message(request)
        
        # Create a prompt for the LLM to determine the user's intent
        prompt = [
            SystemMessage(content=ParseRequestCharacter().get_character()),
            HumanMessage(content=request)
        ]
        
        try:
            # Get the response from the LLM
            response = self.llm.invoke(prompt)
            intent = response.content.strip().lower()
            
            # Validate and normalize the response
            if "generate" in intent:
                action = "generate"
            elif "improve" in intent:
                action = "improve"
            else:
                # Default to generate if unclear
                logger.warning(f"Unclear intent from LLM: {intent}. Defaulting to 'generate'")
                action = "generate"
                
            logger.info(f"Detected user intent: {action}")
            
            # Create the command object
            command = action
            
            return command
            
        except Exception as e:
            logger.error(f"Error determining request intent: {e}")
            # Default to generate in case of errors
            return {"action": "generate", "request": request}
        
    def improve_blog(self, request):
        """
        Process an improvement request for an existing blog post.
        
        Args:
            request: String containing the user's request
        """
        pass


    def User_input(self, user_input):
        """
        Process user input to extract a blog topic using LLM.
        
        Args:
            user_input: User input string containing blog topic ideas
            
        Returns:
            str: Extracted blog topic from user input
        """
        try:
            # Store user input in memory
            self.memory.add_user_message(user_input)
            
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
            logger.warning("No topics provided, cannot extract relevant keyword")
            raise ValueError("No topics provided")
            
        # Use LLM to select the most relevant topic
        prompt = KeywordsCharacter(topic, top_related_topics).get_character()
        keywords_prompt = KeywordListCharacter(topic,top_related_topics).get_character();
        
        response = self.llm.predict(prompt)
        keywordListResponse = self.llm.predict(keywords_prompt)
        relevant_topic = response.strip()
        relevantKeywords = keywordListResponse.strip()
        
        # Validate the response
        if relevant_topic not in top_related_topics:
            logger.warning(f"LLM returned '{relevant_topic}' which is not in the provided topics")
            raise ValueError("Invalid keyword selection")
            
        logger.info(f"Selected relevant topic: {relevant_topic}")
        return relevant_topic, relevantKeywords

    def create_system_prompt(self, topic, blogs_urls, keywords, tone, target_audience, crawled_content):
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
        if crawled_content:
            self.rag_system.add_documents(crawled_content)
        
        # Create an expanded query using the topic and keywords
        expanded_query = f"{topic}"
        
        # Use LLM to refine the search query
        query_refinement_prompt = RefineQueryCharacter(topic).get_character()
        
        # Extract list of relevant keywords
        logger.info(f"Keywords: {keywords}")
        
        refined_query = self.llm.predict(query_refinement_prompt).strip()
        logger.info(f"Refined search query: {refined_query}")
        
        # Retrieve relevant content using the refined query
        rag_content = self.rag_system.retrieve_relevant_content(refined_query, k=5)
        logger.info(f"Retrieved {len(rag_content.split())} words of relevant content")
        
        # Add memory context if available
        memory_context = ""
        if self.memory.conversation_history:
            # Get up to the last 5 messages for context
            recent_messages = self.memory.get_recent_messages(5)
            memory_context = "Previous conversation context:\n"
            for msg in recent_messages:
                memory_context += f"- {msg['role']}: {msg['content']}\n"
        
        # Include memory context in the character prompt
        system_prompt = BlogCharacter(topic, blogs_urls, keywords, tone, target_audience, rag_content, memory_context).get_character()
        
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
        
        # Process the topic to find related queries
        top_related_topics = KeywordsFinder().find_keywords(topic)
        logger.info(f"Found {len(top_related_topics)} related topics")
        
        # Find the most relevant keyword
        relevant_keyword, keyword_list = self.find_relevant_keyword(topic, top_related_topics)
        logger.info(f"Selected relevant keyword: {relevant_keyword}")
        
        # Fetch blogs urls
        logger.info(f"Fetching content for keyword: {relevant_keyword}")
        blogs_urls = BlogLinkFetcher().fetch_all_blogs(relevant_keyword)
        BlogLinkFetcher().save_results(blogs_urls, "blog/link.json")
        
        # Fetch blog content
        crawled_content = BlogContentExtractor().fetch_blog_content(blogs_urls)
        logger.info(f"Fetched {len(crawled_content) if crawled_content else 0} chars of content")
        
        # Create system prompt with RAG content
        tone = "Helpful & Value-Driven"
        target_audience = "general"
        system_prompt = self.create_system_prompt(topic, blogs_urls, keyword_list, tone, target_audience, crawled_content)
        
        # Create message objects
        system_message = SystemMessage(content=system_prompt)
        human_message = HumanMessage(content=user_input)
        
        AI_message = []
        # Stream the response
        async for chunk in self.llm.astream([system_message, human_message]):
            if hasattr(chunk, 'content'):
                yield chunk.content
                AI_message.append(chunk.content)
            elif isinstance(chunk, str):
                yield chunk
                AI_message.append(chunk)
            else:
                yield str(chunk)
                AI_message.append(str(chunk))
        
        collected_chunks = "".join(AI_message)
        self.memory.add_ai_message(collected_chunks)
        
        generation_time = time.time() - start_time
        logger.info(f"Blog generated in {generation_time:.2f}s")

 