"""
LLM Integration for RAG

Handles LLM API calls with streaming support.
Supports both OpenAI and Groq providers.
"""

import os
from typing import Iterator, Optional, List, Dict, Any, Literal
from openai import OpenAI
from dotenv import load_dotenv

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class LLMGenerator:
    """
    Multi-provider LLM wrapper for generating responses.
    
    Supports:
    - OpenAI (gpt-3.5-turbo, gpt-4)
    - Groq (llama-3.3-70b-versatile, llama-3.1-8b-instant) - FREE & FAST
    - Streaming responses
    - Conversation history
    - Configurable model and parameters
    """
    
    def __init__(
        self,
        provider: Literal["groq", "openai"] = "groq",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        api_key: Optional[str] = None,
    ):
        """
        Initialize LLM generator.
        
        Args:
            provider: LLM provider ("groq" or "openai")
            model: Model name (if None, uses provider default)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            api_key: API key (if None, loads from env based on provider)
        """
        # Load environment variables
        load_dotenv()
        
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Set default models
        if model is None:
            if provider == "groq":
                model = "llama-3.3-70b-versatile"  # Free, fast, high quality
            else:
                model = "gpt-3.5-turbo"
        
        self.model = model
        
        # Initialize appropriate client
        if provider == "groq":
            if not GROQ_AVAILABLE:
                raise ImportError(
                    "Groq SDK not installed. Run: pip install groq"
                )
            
            if api_key is None:
                api_key = os.getenv("GROQ_API_KEY")
            
            if not api_key:
                raise ValueError(
                    "Groq API key not found. "
                    "Set GROQ_API_KEY environment variable or pass api_key parameter."
                )
            
            self.client = Groq(api_key=api_key)
        
        elif provider == "openai":
            if api_key is None:
                api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                raise ValueError(
                    "OpenAI API key not found. "
                    "Set OPENAI_API_KEY environment variable or pass api_key parameter."
                )
            
            self.client = OpenAI(api_key=api_key)
        
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'groq' or 'openai'.")
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response
            
        Returns:
            Generated text response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=stream,
        )
        
        if stream:
            # This shouldn't happen in non-stream mode, but handle it
            chunks = []
            for chunk in response:
                if chunk.choices[0].delta.content:
                    chunks.append(chunk.choices[0].delta.content)
            return "".join(chunks)
        else:
            return response.choices[0].message.content
    
    def generate_stream(
        self,
        messages: List[Dict[str, str]],
    ) -> Iterator[str]:
        """
        Generate a streaming response from the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Yields:
            Text chunks as they're generated
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class ConversationMemory:
    """
    Manages conversation history for multi-turn interactions.
    
    Keeps track of messages, handles context window limits, and tracks
    conversation context like active guests/speakers.
    """
    
    def __init__(self, max_messages: int = 10):
        """
        Initialize conversation memory.
        
        Args:
            max_messages: Maximum number of messages to keep (excludes system message)
        """
        self.max_messages = max_messages
        self.system_message = None
        self.messages = []
        
        # Conversation context tracking
        self.active_guests = []  # List of guests from recent responses
        self.recent_topics = []  # List of recent topics/themes discussed
    
    def set_system_message(self, content: str):
        """Set the system message (instructions for the LLM)."""
        self.system_message = {"role": "system", "content": content}
    
    def add_user_message(self, content: str):
        """Add a user message to history."""
        self.messages.append({"role": "user", "content": content})
        self._trim_history()
    
    def add_assistant_message(self, content: str):
        """Add an assistant message to history."""
        self.messages.append({"role": "assistant", "content": content})
        self._trim_history()
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get all messages for sending to LLM.
        
        Returns:
            List of message dicts including system message
        """
        if self.system_message:
            return [self.system_message] + self.messages
        return self.messages
    
    def clear(self):
        """Clear conversation history (keeps system message)."""
        self.messages = []
        self.active_guests = []
        self.recent_topics = []
    
    def update_context(self, guests: List[str], topics: Optional[List[str]] = None):
        """
        Update conversation context with guests and topics from recent response.
        
        Args:
            guests: List of guest names mentioned in the response
            topics: Optional list of topics discussed
        """
        # Update active guests (keep unique, most recent first)
        for guest in guests:
            if guest in self.active_guests:
                self.active_guests.remove(guest)
            self.active_guests.insert(0, guest)
        
        # Keep only the 3 most recent guests
        self.active_guests = self.active_guests[:3]
        
        # Update topics if provided
        if topics:
            for topic in topics:
                if topic in self.recent_topics:
                    self.recent_topics.remove(topic)
                self.recent_topics.insert(0, topic)
            # Keep only the 5 most recent topics
            self.recent_topics = self.recent_topics[:5]
    
    def get_active_guest(self) -> Optional[str]:
        """
        Get the most recently discussed guest.
        
        Returns:
            Guest name or None if no guests in context
        """
        return self.active_guests[0] if self.active_guests else None
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """
        Get the current conversation context.
        
        Returns:
            Dict with active guests and recent topics
        """
        return {
            "active_guests": self.active_guests,
            "recent_topics": self.recent_topics,
            "has_context": len(self.active_guests) > 0 or len(self.recent_topics) > 0,
        }
    
    def _trim_history(self):
        """Keep only the most recent messages."""
        if len(self.messages) > self.max_messages:
            # Keep pairs of user/assistant messages
            self.messages = self.messages[-self.max_messages:]


def create_rag_messages(
    query: str,
    context: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> List[Dict[str, str]]:
    """
    Create messages for RAG query.
    
    Args:
        query: User's question
        context: Retrieved context from vector database
        conversation_history: Optional previous messages
        
    Returns:
        List of messages for LLM
    """
    system_message = """You are a helpful AI assistant that answers questions about the WTF Podcast episodes. 

Your job is to:
1. Answer questions based on the provided podcast transcript excerpts
2. Be specific and cite which guest said what when relevant
3. If the context doesn't contain enough information, say so honestly
4. Keep answers concise but informative
5. Use a friendly, conversational tone

Remember: Only use information from the provided context. Don't make up information."""

    user_message = f"""Context from podcast transcripts:
{context}

Question: {query}

Please provide a helpful answer based on the context above."""

    messages = [{"role": "system", "content": system_message}]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current query
    messages.append({"role": "user", "content": user_message})
    
    return messages


if __name__ == "__main__":
    # Test LLM (requires API key)
    print("🧪 Testing LLM Generator\n")
    
    try:
        # Test Groq first (free!)
        print("=" * 60)
        print("Testing Groq (llama-3.3-70b-versatile)")
        print("=" * 60)
        
        llm = LLMGenerator(provider="groq")
        
        # Test simple generation
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, world!' in a creative way."},
        ]
        
        print("\nTesting non-streaming generation...")
        response = llm.generate(messages)
        print(f"Response: {response}\n")
        
        print("Testing streaming generation...")
        print("Response: ", end="", flush=True)
        for chunk in llm.generate_stream(messages):
            print(chunk, end="", flush=True)
        print("\n")
        
        # Test conversation memory
        print("\nTesting conversation memory...")
        memory = ConversationMemory()
        memory.set_system_message("You are a helpful assistant.")
        memory.add_user_message("What is 2+2?")
        memory.add_assistant_message("2+2 equals 4.")
        
        print(f"Messages in memory: {len(memory.get_messages())}")
        print("✓ LLM test complete")
        
    except ValueError as e:
        print(f"⚠️  {e}")
        print("\nTo test LLM, create a .env file with:")
        print("GROQ_API_KEY=your-key-here (FREE at https://console.groq.com)")
        print("OR")
        print("OPENAI_API_KEY=your-key-here")

