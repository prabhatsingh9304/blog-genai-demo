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
    def __init__(self, model_name="gpt-4o", rag_system=None, use_openrouter=True, temperature=0.7):
        """
        Initialize the BlogAgent with a language model and RAG system
        
        Args:
            model_name (str): The model to use (default: "gpt-4o")
            rag_system (RAGSystem): An instance of the RAG system
            use_openrouter (bool): Whether to use OpenRouter API for accessing models
            temperature (float): Temperature for generation (default: 0.7)
        """
        self.rag_system = rag_system or RAGSystem()
        
        # Configure LLM with OpenRouter or OpenAI
        if use_openrouter:
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            
            if not openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is required")
            
            # Define client parameters once
            client_params = {
                "openai_api_key": openrouter_api_key,
                "openai_api_base": "https://openrouter.ai/api/v1",
                "default_headers": {
                    "HTTP-Referer": "https://blog-generation-app.com",
                    "X-Title": "Blog Generation with RAG"
                }
            }
            
            self.llm = ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                **client_params
            )
        else:
            # Standard OpenAI configuration
            self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        
        # Make a list of trending keywords
        self.trending_keywords = [
            "Artificial Intelligence", "Machine Learning", "LLM Applications",
            "ChatGPT", "Generative AI", "Neural Networks", "Natural Language Processing",
            "Computer Vision", "Reinforcement Learning", "AI Ethics", "Data Science",
            "Transformer Models", "Deep Learning", "Prompt Engineering", "RAG Systems"
        ]
        
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
            str: The most relevant keyword from the trending keywords list
        """
        response = self.keyword_chain.invoke({
            "topic": topic,
            "trending_keywords": self.trending_keywords
        })
        return response["text"].strip()

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
        Use the following reference information to create a concise blog post:
        
        {rag_content}
        
        Write in a conversational tone. Structure with:
        - Brief introduction (1 paragraph)
        - 2-3 key points (1 paragraph each)
        - Short conclusion (1 paragraph)
        Keep total length under 500 words. Avoid technical jargon.
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
default_agent = BlogAgent(use_openrouter=True, temperature=0.7)

# For backward compatibility - these functions call the default agent's methods
def find_relevant_keyword(topic):
    return default_agent.find_relevant_keyword(topic)

def create_system_message(topic, relevant_keyword):
    return default_agent.create_system_message(topic, relevant_keyword)

def generate_blog(topic):
    return default_agent.generate_blog(topic)
 