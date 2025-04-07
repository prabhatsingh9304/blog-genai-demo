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
from blog.process import Process
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('blog_agent')

# Load environment variables
load_dotenv()

class BlogAgent:
    """
    Agent for generating blog content using LLMs and RAG.
    """
    def __init__(self, model_name="gpt-4", rag_system=None, temperature=0.7):
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
                streaming=True  # Enable streaming
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
            prompt = f"""
            Extract the main blog topic from the following user input:  
            "{user_input}"  

            Ensure the extracted topic is concise, relevant, and properly formatted for a blog title.  
            Return only the topic name—no explanations.  

            """
            
            topic = self.llm.predict(prompt).strip()
            logger.info(f"Extracted topic from user input: {topic}")
            return topic
        except Exception as e:
            logger.error(f"Error extracting topic from user input: {e}")
            # Return original input as fallback
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
            prompt = f"""            
            From these trending topics: {', '.join(top_related_topics)},  
            select the **most relevant and engaging** one for a blog on "{topic}".  
            Return only the topic name—no explanations.  
            """
            
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

    def create_system_prompt(self, topic, crawled_content=None):
        """
        Create a system prompt with RAG content for blog generation.
        
        Args:
            topic: The main blog topic
            crawled_content: Optional crawled content to add to RAG
            
        Returns:
            str: A system prompt for the LLM
        """
        start_time = time.time()
        
        # Add crawled content to RAG if provided
        if crawled_content and crawled_content.strip():
            logger.info(f"Adding {len(crawled_content)} chars of crawled content to RAG")
            self.rag_system.add_documents(crawled_content)
        
        # Retrieve relevant content for the topic
        logger.info(f"Retrieving content relevant to: {topic}")
        rag_content = self.rag_system.retrieve_relevant_content(topic)
        
        # Build the prompt
        system_prompt = f"""
        Write a high-quality, SEO-optimized blog post on **{topic}** that is engaging, informative, and designed to rank well on search engines. The blog should be structured for readability and user engagement while demonstrating deep expertise.  

        ### **Requirements:**  
        ✔ **Word Count:** At least **1,000 words**  
        ✔ **Readability:** Aim for a Flesch Reading Ease score of **50+** (clear and accessible writing)  
        ✔ **Structure:** Use clear **H2 & H3 subheadings** for better organization and SEO  
        ✔ **Paragraph Length:** Keep paragraphs under **150 words** for easy reading  
        ✔ **Sentence Length:** Ensure **75%+ of sentences have 20 words or fewer**  
        ✔ **Transition Words:** Use transition words in at least **30% of sentences** to improve flow  
        ✔ **Passive Voice:** Keep passive voice below **10%** for clarity  

        ### **Blog Structure:**  

        #### **1. Engaging Introduction (1-2 Short Paragraphs)**  
        - Hook the reader with a **compelling fact, question, or bold statement**  
        - Establish **authority and relevance**—explain why this topic matters  
        - Briefly outline what readers will learn  

        #### **2. Well-Structured Key Sections (4-6 H2 Subheadings)**  
        - Each section should provide **valuable insights, expert analysis, and real-world examples**  
        - Use **bullet points and lists** for better readability  
        - Keep content **concise, actionable, and engaging**  

        #### **3. Data, Case Studies, and Examples**  
        - Incorporate **statistics, case studies, or real-world applications** to enhance credibility  
        - Use **quotes from experts** or industry references if applicable  

        #### **4. Actionable Takeaways & Conclusion (1-2 Paragraphs)**  
        - Summarize key points and insights  
        - Provide **actionable recommendations** that readers can implement immediately  
        - End with a **call to action** (e.g., comment, share, explore related content)  

        ### **SEO Best Practices:**  
            **Use Primary & Secondary Keywords Naturally**—avoid keyword stuffing  
            **Include Internal & External Links** for credibility and engagement  
            **Write in a Conversational Yet Professional Tone**  
            **Ensure Mobile-Friendliness**—short paragraphs, scannable text, and engaging formatting  

        This blog should be **so valuable that readers consider it the ultimate resource on {topic} and feel compelled to share it.**"  

        Use these valuable research insights to enrich your content: {rag_content} 
        """
        
        
        logger.info(f"System prompt created in {time.time() - start_time:.2f}s")
        return system_prompt

    def generate_blog(self, topic, user_input):
        """
        Generate a blog based on the given topic.
        
        Args:
            topic: The topic to generate a blog about
            
        Returns:
            dict: A dictionary containing the topic and generated content
        """
        start_time = time.time()
        logger.info(f"Generating blog on topic: {topic}")
        
        try:
            # Process the topic to find related queries
            process = Process(topic)
            top_related_topics = process.find_top_queries()
            logger.info(f"Found {len(top_related_topics)} related topics")
            
            # Find the most relevant keyword
            relevant_keyword = self.find_relevant_keyword(top_related_topics)
            logger.info(f"Selected relevant keyword: {relevant_keyword}")
            
            # Fetch blog content using the relevant keyword
            logger.info(f"Fetching content for keyword: {relevant_keyword}")
            crawled_content = process.fetch_blog_content(relevant_keyword)
            logger.info(f"Fetched {len(crawled_content) if crawled_content else 0} chars of content")
            
            # Create system prompt with RAG content
            system_prompt = self.create_system_prompt(topic, crawled_content)
            
            # Generate blog using LLM
            blog_content = self._generate_blog_content(topic, system_prompt, user_input)
            
            generation_time = time.time() - start_time
            logger.info(f"Blog generated in {generation_time:.2f}s")
            
            return {
                "topic": topic,
                "content": blog_content,
                "generation_time": generation_time
            }
            
        except Exception as e:
            logger.error(f"Error generating blog: {e}")
            return {
                "topic": topic,
                "content": f"Error generating blog: {str(e)}",
                "error": True
            }
            
    def _generate_blog_content(self, topic, system_prompt, user_input):
        """Generate blog content using the LLM."""
        try:
            logger.info("Generating blog with LLM")
            
            # Create message objects
            system_message = SystemMessage(content=system_prompt)
            human_message = HumanMessage(content=user_input)
            
            # Invoke the LLM
            result = self.llm.invoke([system_message, human_message])
            
            # Extract content from result
            if hasattr(result, 'content'):
                blog_content = result.content
            elif isinstance(result, str):
                blog_content = result
            else:
                # Try to get content from messages
                blog_content = result.messages[-1].content if hasattr(result, 'messages') else str(result)
                
            logger.info(f"Generated blog with {len(blog_content)} chars")
            return blog_content
            
        except Exception as e:
            logger.error(f"Error in primary generation: {e}")
            return self._fallback_generation(topic, system_prompt)
    
    def _fallback_generation(self, topic, system_prompt):
        """Fallback generation method."""
        try:
            logger.info("Using fallback generation method")
            simple_prompt = f"Write a comprehensive blog post about {topic}. " + system_prompt
            
            result = self.llm.invoke(simple_prompt)
            
            if hasattr(result, 'content'):
                return result.content
            else:
                return str(result)
                
        except Exception as fallback_error:
            logger.error(f"Fallback generation failed: {fallback_error}")
            
            # Last resort - return mock content
            return f"""# {topic}

## Introduction
This is a sample blog post about {topic}. Due to technical limitations, we're providing this placeholder content.

## Key Points
- {topic} is an important area with significant developments
- Understanding {topic} requires careful consideration of various factors
- Many experts believe {topic} will continue to evolve in coming years

## Conclusion
As we've seen, {topic} presents both challenges and opportunities. This placeholder content is provided because of a technical error during content generation.
"""

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
            process = Process(topic)
            top_related_topics = process.find_top_queries()
            logger.info(f"Found {len(top_related_topics)} related topics")
            
            # Find the most relevant keyword
            relevant_keyword = self.find_relevant_keyword(topic, top_related_topics)
            logger.info(f"Selected relevant keyword: {relevant_keyword}")
            
            # Fetch blog content using the relevant keyword
            logger.info(f"Fetching content for keyword: {relevant_keyword}")
            crawled_content = process.fetch_blog_content(relevant_keyword)
            logger.info(f"Fetched {len(crawled_content) if crawled_content else 0} chars of content")
            
            # Create system prompt with RAG content
            system_prompt = self.create_system_prompt(topic, crawled_content)
            
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
default_agent = BlogAgent(temperature=0.7)

# For backward compatibility - these functions call the default agent's methods
def find_relevant_keyword(topic):
    return default_agent.find_relevant_keyword(topic)

def create_system_message(topic, relevant_keyword=None):
    return default_agent.create_system_prompt(topic)

def generate_blog(topic):
    return default_agent.generate_blog(topic)
 