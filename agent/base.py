from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document
from langchain_community.llms.fake import FakeListLLM
from langchain_core.messages import HumanMessage, SystemMessage
import os
import sys
from rag.rag import RAGSystem
from dotenv import load_dotenv
import json
from ..blog.process import Process

load_dotenv()

class BlogAgent:
    def __init__(self, model_name="gpt-4", rag_system=None, temperature=0.7):
        """
        Initialize with OpenAI API
        """
        # Get API key 
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        if not api_key:
            print("WARNING: No API key found. Using demo mode with mock responses.")
            responses = [
                "Artificial Intelligence",
                "This is a sample blog post about the topic. AI has transformed many industries including healthcare, finance, and education. It continues to evolve rapidly with new developments in machine learning and neural networks.",
                "Machine Learning"
            ]
            self.llm = FakeListLLM(responses=responses)
        else:
            print(f"Using OpenAI API with model: {model_name}")
            # Initialize LLM with OpenAI API
            try:
                self.llm = ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature,
                    openai_api_key=api_key
                )
                # Test the model to ensure it works - using a simple string instead of a message
                test_result = self.llm.invoke("Write one sentence about AI.")
                print(f"LLM test successful: Model {model_name} is working")
            except Exception as e:
                error_msg = str(e)
                print(f"WARNING: Error initializing OpenAI ChatModel: {error_msg}")
                
                # Check if this is a model access error
                if "does not exist" in error_msg or "not found" in error_msg:
                    print(f"Model {model_name} not found, falling back to gpt-3.5-turbo")
                    try:
                        self.llm = ChatOpenAI(
                            model_name="gpt-3.5-turbo",
                            temperature=temperature,
                            openai_api_key=api_key
                        )
                        print("Successfully initialized fallback model gpt-3.5-turbo")
                    except Exception as fallback_error:
                        print(f"ERROR: Could not initialize fallback model: {fallback_error}")
                        print("Using demo mode with mock responses")
                        responses = [
                            "Artificial Intelligence",
                            "This is a sample blog post about the topic. AI has transformed many industries including healthcare, finance, and education.",
                            "Machine Learning"
                        ]
                        self.llm = FakeListLLM(responses=responses)
                # Check if this is a quota error
                elif "quota" in error_msg.lower() or "429" in error_msg:
                    print("WARNING: OpenAI API quota exceeded.")
                    print("Using demo mode with mock responses until quota is restored")
                    responses = [
                        "Artificial Intelligence",
                        "This is a sample blog post about the topic. AI has transformed many industries including healthcare, finance, and education.",
                        "Machine Learning"
                    ]
                    self.llm = FakeListLLM(responses=responses)
                else:
                    print("Using demo mode with mock responses")
                    responses = [
                        "Artificial Intelligence",
                        "This is a sample blog post about the topic. AI has transformed many industries including healthcare, finance, and education.",
                        "Machine Learning"
                    ]
                    self.llm = FakeListLLM(responses=responses)
        
        self.rag_system = rag_system or RAGSystem()
        

    def find_relevant_keyword(self, topic):
        """
        Extract a keyword from the topic itself
        
        Args:
            topic (str): The topic to find a relevant keyword for
            
        Returns:
            str: A keyword derived from the topic
        """
        # Simply use the topic as the keyword or extract the main subject
        # Split by common separators and take the first meaningful word
        
        # topic is a list of topics... make llm call and retrieve relavent topic
        #find link
        relevant_topic = "test"
        blog_content = Process(relevant_topic).fetch_blog_content()

    def create_system_prompt(self, topic, relevant_keyword):
        """
        Create a system prompt with RAG content for the blog generation
        
        Args:
            topic (str): The blog topic
            relevant_keyword (str): The identified relevant keyword
            
        Returns:
            str: A system prompt for the LLM
        """
        rag_content = self.rag_system.retrieve_relevant_content(topic)
        
        system_prompt = f"""
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
        
        return system_prompt

    def generate_blog(self, topic):
        """
        Generate a blog based on the given topic
        
        Args:
            topic (str): The topic to generate a blog about
            
        Returns:
            dict: A dictionary containing the topic and generated content
        """
        # Extract a simple keyword from the topic
        top_related_topics = Process(topic).find_top_queries()
        relevant_keyword = self.find_relevant_keyword(top_related_topics)
        
        # Create system message with RAG content
        system_prompt = self.create_system_prompt(topic, relevant_keyword)
        
        # Generate blog using LLM with newer format
        try:
            # Create proper SystemMessage and HumanMessage objects
            system_message = SystemMessage(content=system_prompt)
            human_message = HumanMessage(content=f"Write a comprehensive blog post about {topic}.")
            
            # Invoke the LLM with proper message objects
            result = self.llm.invoke([system_message, human_message])
            
            # Extract the content from the result
            if hasattr(result, 'content'):
                blog_content = result.content
            elif isinstance(result, str):
                blog_content = result
            else:
                # Try to get the content from the last message
                blog_content = result.messages[-1].content if hasattr(result, 'messages') else str(result)
            
        except Exception as e:
            print(f"Error generating blog: {e}")
            # Fallback to a simpler string prompt
            try:
                simple_prompt = f"Write a comprehensive blog post about {topic}. " + system_prompt
                result = self.llm.invoke(simple_prompt)
                if hasattr(result, 'content'):
                    blog_content = result.content
                else:
                    blog_content = str(result)
            except Exception as fallback_error:
                print(f"Fallback error: {fallback_error}")
                # Last resort - return mock content
                blog_content = f"""# {topic}

## Introduction
This is a sample blog post about {topic}. Due to API limitations, we're providing this placeholder content.

## Key Points
- {topic} is an important area with significant developments
- Understanding {topic} requires careful consideration of various factors
- Many experts believe {topic} will continue to evolve in coming years

## Conclusion
As we've seen, {topic} presents both challenges and opportunities. This placeholder content is provided because your OpenAI API quota has been exceeded.
"""
        
        return {
            "topic": topic,
            "content": blog_content
        }

# Instantiate a default agent for backward compatibility
default_agent = BlogAgent(temperature=0.7)

# For backward compatibility - these functions call the default agent's methods
def find_relevant_keyword(topic):
    return default_agent.find_relevant_keyword(topic)

def create_system_message(topic, relevant_keyword):
    return default_agent.create_system_prompt(topic, relevant_keyword)

def generate_blog(topic):
    return default_agent.generate_blog(topic)
 