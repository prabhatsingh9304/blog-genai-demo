from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('agent_memory')

class AgentMemory:
    """
    Memory system for the BlogAgent to maintain conversation history and context.
    """
    def __init__(self, 
                session_id: str = None,
                max_token_limit: int = 2000,
                k: int = 5):
        """
        Initialize the agent memory system.
        
        Args:
            session_id: Unique identifier for the conversation session
            max_token_limit: Maximum number of tokens to store in memory
            k: Number of recent conversations to keep in window memory
        """
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.max_token_limit = max_token_limit
        
        # Initialize different types of memory
        self.buffer_memory = ConversationBufferMemory(
            return_messages=True,
            output_key="output",
            input_key="input"
        )
        
        self.window_memory = ConversationBufferWindowMemory(
            k=k,
            return_messages=True,
            output_key="output",
            input_key="input"
        )
        
        self.conversation_history: List[Dict] = []

    def add_user_message(self, message: str) -> None:
        """
        Add a user message to memory.
        
        Args:
            message: The user's message
        """
        try:
            # Add to buffer memory
            self.buffer_memory.save_context(
                {"input": message},
                {"output": ""}
            )
            
            # Add to window memory
            self.window_memory.save_context(
                {"input": message},
                {"output": ""}
            )
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"User message added to memory: {message[:50]}...")
            
        except Exception as e:
            logger.error(f"Error adding user message to memory: {e}")

    def add_ai_message(self, message: str) -> None:
        """
        Add an AI message to memory.
        
        Args:
            message: The AI's response message
        """
        try:
            # Add to buffer memory
            self.buffer_memory.save_context(
                {"input": ""},
                {"output": message}
            )
            
            # Add to window memory
            self.window_memory.save_context(
                {"input": ""},
                {"output": message}
            )
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"AI message added to memory: {message[:50]}...")
            
        except Exception as e:
            logger.error(f"Error adding AI message to memory: {e}")

    def get_recent_messages(self, k: int = None) -> List[Dict]:
        """
        Get the k most recent messages from memory.
        
        Args:
            k: Number of recent messages to retrieve (default: window memory size)
            
        Returns:
            List of recent messages
        """
        k = k or self.window_memory.k
        return self.conversation_history[-k:]

    def clear_memory(self) -> None:
        """Clear all memory stores."""
        try:
            self.buffer_memory.clear()
            self.window_memory.clear()
            self.conversation_history = []
            logger.info("Memory cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")

    def save_to_file(self, filepath: str = None) -> None:
        """
        Save conversation history to a JSON file.
        
        Args:
            filepath: Path to save the file (default: session_id based)
        """
        try:
            if not filepath:
                filepath = f"conversation_history_{self.session_id}.json"
            
            with open(filepath, 'w') as f:
                json.dump({
                    "session_id": self.session_id,
                    "history": self.conversation_history
                }, f, indent=2)
            
            logger.info(f"Conversation history saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving conversation history: {e}")

    def load_from_file(self, filepath: str) -> None:
        """
        Load conversation history from a JSON file.
        
        Args:
            filepath: Path to the history file
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.session_id = data.get("session_id", self.session_id)
                self.conversation_history = data.get("history", [])
                
            # Rebuild other memory stores from loaded history
            for message in self.conversation_history:
                if message["role"] == "user":
                    self.buffer_memory.save_context(
                        {"input": message["content"]},
                        {"output": ""}
                    )
                else:
                    self.buffer_memory.save_context(
                        {"input": ""},
                        {"output": message["content"]}
                    )
            
            logger.info(f"Conversation history loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")

    def get_memory_variables(self) -> dict:
        """
        Get all variables stored in memory.
        
        Returns:
            Dictionary of memory variables
        """
        return {
            "buffer_memory": self.buffer_memory.load_memory_variables({}),
            "window_memory": self.window_memory.load_memory_variables({}),
            "history": self.conversation_history
        }
