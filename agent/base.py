from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.schema import SystemMessage, HumanMessage
import os
import sys

# Add the parent directory to the system path to import from rag module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.rag import RAGSystem

class BlogAgent:
    def __init__(self, model_name="gpt-4", rag_system=None, temperature=0.7):
        """
        Initialize with OpenAI API
        """
        # Get API key 
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        if not api_key:
            print("WARNING: No API key found. Using demo mode with mock responses.")
            from langchain.llms.fake import FakeListLLM
            responses = [
                "Artificial Intelligence",
                "This is a sample blog post about the topic. AI has transformed many industries including healthcare, finance, and education. It continues to evolve rapidly with new developments in machine learning and neural networks.",
                "Machine Learning"
            ]
            self.llm = FakeListLLM(responses=responses)
            
        # Check if this is an OpenRouter API key
        elif api_key.startswith("sk-or-v1-"):
            print("Using OpenRouter API")
            # Initialize LLM with OpenRouter API
            self.llm = ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                openai_api_key=api_key,
                openai_api_base="https://openrouter.ai/api/v1"
            )
        else:
            print("Using OpenAI API")
            # Initialize LLM with OpenAI API
            self.llm = ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                openai_api_key=api_key
            )
        
        self.rag_system = rag_system or RAGSystem()
        
        # Start with an empty list of trending keywords that will be populated dynamically
        self.trending_keywords = []
        
        # Try to load trending keywords from blog/trends.py
        try:
            from blog.trends import get_trending_topics
            self.trending_keywords = get_trending_topics(limit=15)
            if not self.trending_keywords:  # If still empty, add a minimal set
                self.trending_keywords = ["Technology", "Innovation", "Digital Transformation"]
        except Exception as e:
            print(f"Note: Could not load trending topics: {e}")
            # Minimal fallback list if needed
            self.trending_keywords = ["Technology", "Innovation", "Digital Transformation"]
        
        # Create a prompt template to find one relevant keyword
        self.keyword_prompt_template = PromptTemplate(
            input_variables=["topic", "trending_keywords"],
            template="""
            You are an AI assistant specialized in identifying relevant keywords for blog topics.
            Given the user's topic: "{topic}", 
            and this list of trending keywords: {trending_keywords},
            select the SINGLE most relevant keyword from the list that aligns best with the user's topic.
            Return only the keyword without any additional text.
            """
        )
        
        # Initialize keyword chain
        self.keyword_chain = LLMChain(llm=self.llm, prompt=self.keyword_prompt_template)

    def add_trending_keywords(self, keywords):
        """
        Add new keywords to the trending keywords list
        
        Args:
            keywords (list): List of new keywords to add
        
        Returns:
            list: Updated trending keywords list
        """
        for keyword in keywords:
            if keyword not in self.trending_keywords:
                self.trending_keywords.append(keyword)
        return self.trending_keywords
    
    def get_trending_keywords(self, limit=None):
        """
        Get the list of trending keywords
        
        Args:
            limit (int): Optional limit for the number of keywords to return
        
        Returns:
            list: List of trending keywords
        """
        if limit:
            return self.trending_keywords[:limit]
        return self.trending_keywords
    
    def find_relevant_keyword(self, topic):
        """
        Find the most relevant keyword for a given topic
        
        Args:
            topic (str): The topic to find a relevant keyword for
            
        Returns:
            str: The most relevant keyword from the trending keywords list or derived from the topic
        """
        # If we have trending keywords, use the chain to find the most relevant
        if self.trending_keywords:
            response = self.keyword_chain.invoke({
                "topic": topic,
                "trending_keywords": self.trending_keywords
            })
            return response["text"].strip()
        
        # If no trending keywords are available, extract a keyword from the topic itself
        # Try to get related topics from content analyzer
        try:
            from blog.content_analyzer import get_related_topics
            related = get_related_topics(topic, limit=1)
            if related:
                return related[0]
        except:
            pass
            
        # If all else fails, use the topic as the keyword
        return topic.strip()

    def create_system_message(self, topic, relevant_keyword):
        """
        Create a system message with RAG content for the blog generation
        
        Args:
            topic (str): The blog topic
            relevant_keyword (str): The identified relevant keyword
            
        Returns:
            SystemMessage: A system message for the LLM
        """
        rag_content = self.rag_system.retrieve_relevant_content(topic)
        
        system_message = f"""
        You are an expert blog writer specializing in {relevant_keyword}.
        Use the following reference information to create a comprehensive blog post:
        
        {rag_content}
        
        Write in a conversational yet authoritative tone. Structure with:
        - Engaging introduction (1-2 paragraphs)
        - 4-6 substantial key points with detailed explanations (2-3 paragraphs each)
        - Examples, case studies, or data points to support your arguments
        - Actionable insights or takeaways for the reader
        - Strong conclusion summarizing the main points (1-2 paragraphs)
        
        Ensure the blog is AT LEAST 1,000 words. Use headings to organize content.
        Balance depth with readability, using industry terminology appropriately.
        """
        
        return SystemMessage(content=system_message)

    def generate_blog(self, topic):
        """
        Generate a blog based on the given topic
        
        Args:
            topic (str): The topic to generate a blog about
            
        Returns:
            dict: A dictionary containing the topic, relevant keyword, and generated content
        """
        # Find the most relevant trending keyword
        relevant_keyword = self.find_relevant_keyword(topic)
        
        # Create system message with RAG content
        system_msg = self.create_system_message(topic, relevant_keyword)
        
        # Create human message with the user's topic
        human_msg = HumanMessage(content=f"Write a comprehensive blog post about {topic}.")
        
        # Generate blog using LLM
        blog_content = self.llm.predict_messages([system_msg, human_msg])
        
        return {
            "topic": topic,
            "relevant_keyword": relevant_keyword,
            "content": blog_content.content
        }

# Instantiate a default agent for backward compatibility with OpenRouter
default_agent = BlogAgent(temperature=0.7)

# For backward compatibility - these functions call the default agent's methods
def find_relevant_keyword(topic):
    return default_agent.find_relevant_keyword(topic)

def create_system_message(topic, relevant_keyword):
    return default_agent.create_system_message(topic, relevant_keyword)

def generate_blog(topic):
    return default_agent.generate_blog(topic)
 