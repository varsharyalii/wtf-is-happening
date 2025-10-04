"""
Prompt Engineering for RAG

Smart context assembly and prompt construction.
"""

from typing import List, Optional
from src.retriever import RetrievalResult
from config.prompts import SYSTEM_PROMPT


class PromptBuilder:
    """
    Builds optimized prompts for RAG queries.
    
    Handles:
    - Context assembly from retrieval results
    - Source attribution
    - Token management
    """
    
    def __init__(
        self,
        max_context_length: int = 3000,  # characters
        include_metadata: bool = True,
    ):
        """
        Initialize prompt builder.
        
        Args:
            max_context_length: Maximum characters in context
            include_metadata: Whether to include guest/episode info
        """
        self.max_context_length = max_context_length
        self.include_metadata = include_metadata
    
    def build_context(
        self,
        results: List[RetrievalResult],
    ) -> str:
        """
        Build context string from retrieval results.
        
        Args:
            results: List of retrieval results
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant context found."
        
        context_parts = []
        current_length = 0
        
        for idx, result in enumerate(results, 1):
            # Build context chunk with metadata
            if self.include_metadata:
                chunk = (
                    f"[Source {idx}: {result.guest} - {result.guest_expertise}]\n"
                    f"{result.text}\n"
                )
            else:
                chunk = f"{result.text}\n"
            
            # Check if adding this chunk would exceed limit
            if current_length + len(chunk) > self.max_context_length:
                # Truncate if this is the first chunk, otherwise skip
                if idx == 1:
                    remaining = self.max_context_length - current_length
                    chunk = chunk[:remaining] + "...\n"
                    context_parts.append(chunk)
                break
            
            context_parts.append(chunk)
            current_length += len(chunk)
        
        return "\n".join(context_parts)
    
    def build_system_prompt(self) -> str:
        """
        Build the system prompt for the LLM.
        
        Pulls from config/prompts.py so you can easily change it.
        
        Returns:
            System prompt string
        """
        # Use the prompt from config file
        # If you want to change the behavior, edit config/prompts.py
        return SYSTEM_PROMPT
    
    def build_user_prompt(
        self,
        query: str,
        context: str,
        previous_context: Optional[str] = None,
    ) -> str:
        """
        Build the user prompt with query and context.
        
        Args:
            query: User's question
            context: Retrieved context
            previous_context: Optional context from previous turn
            
        Returns:
            User prompt string
        """
        parts = []
        
        # Add context - keep it simple and conversational
        parts.append("Here are 3 relevant moments from the podcast:\n\n")
        parts.append(context)
        parts.append("\n")
        
        # Add previous context if this is a follow-up
        if previous_context:
            parts.append("\n=== PREVIOUS CONTEXT ===")
            parts.append(previous_context)
            parts.append("=== END PREVIOUS CONTEXT ===\n")
        
        # Add the actual question
        parts.append(f"\nQuestion: {query}\n")
        
        return "\n".join(parts)
    
    def build_sources_summary(
        self,
        results: List[RetrievalResult],
    ) -> str:
        """
        Build a summary of sources for display.
        
        Args:
            results: List of retrieval results
            
        Returns:
            Formatted sources string
        """
        if not results:
            return "No sources."
        
        # Group by guest
        guests = {}
        for result in results:
            if result.guest not in guests:
                guests[result.guest] = {
                    "expertise": result.guest_expertise,
                    "url": result.youtube_url,
                    "chunks": 0,
                }
            guests[result.guest]["chunks"] += 1
        
        # Format output
        lines = ["\n📚 Sources:"]
        for guest, info in guests.items():
            lines.append(
                f"  • {guest} ({info['expertise']}) - {info['chunks']} excerpt(s)"
            )
            lines.append(f"    {info['url']}")
        
        return "\n".join(lines)


def extract_keywords(query: str) -> List[str]:
    """
    Extract potential keywords from a query for filtering.
    
    This is a simple implementation. Could be enhanced with NLP.
    
    Args:
        query: User's query
        
    Returns:
        List of potential keywords
    """
    # Common stop words to ignore
    stop_words = {
        "what", "when", "where", "who", "why", "how", "is", "are", "was", "were",
        "the", "a", "an", "in", "on", "at", "to", "for", "of", "with", "about",
        "tell", "me", "please", "can", "you", "i", "my"
    }
    
    # Simple tokenization and filtering
    words = query.lower().split()
    keywords = [w.strip("?,!.") for w in words if w.lower() not in stop_words]
    
    return keywords


if __name__ == "__main__":
    # Test prompt builder
    from src.retriever import RetrievalResult
    
    print("🧪 Testing Prompt Builder\n")
    
    # Create dummy results
    dummy_results = [
        RetrievalResult(
            text="Artificial intelligence is going to transform every industry. We're just at the beginning.",
            score=0.85,
            guest="Sam Altman",
            episode_id="ep_001",
            youtube_url="https://youtube.com/watch?v=test1",
            chunk_index=5,
            guest_expertise="CEO, OpenAI",
            industry_tags=["AI", "technology"],
            episode_themes=["innovation"],
            date="2024-01-01",
        ),
        RetrievalResult(
            text="The key to success in tech is building products people actually want to use.",
            score=0.72,
            guest="Dara Khosrowshahi",
            episode_id="ep_002",
            youtube_url="https://youtube.com/watch?v=test2",
            chunk_index=12,
            guest_expertise="CEO, Uber",
            industry_tags=["mobility", "technology"],
            episode_themes=["product"],
            date="2024-01-15",
        ),
    ]
    
    builder = PromptBuilder()
    
    # Test context building
    context = builder.build_context(dummy_results)
    print("Context:")
    print(context)
    print("\n" + "="*80 + "\n")
    
    # Test full prompt
    query = "What do the guests think about AI and technology?"
    user_prompt = builder.build_user_prompt(query, context)
    print("User Prompt:")
    print(user_prompt)
    print("\n" + "="*80 + "\n")
    
    # Test sources summary
    sources = builder.build_sources_summary(dummy_results)
    print("Sources Summary:")
    print(sources)
    print("\n" + "="*80 + "\n")
    
    # Test keyword extraction
    keywords = extract_keywords("What did Sam Altman say about the future of AI?")
    print(f"Keywords: {keywords}")
    
    print("\n✓ Prompt builder test complete")

