"""
Query Service - Complete RAG Pipeline

Orchestrates retrieval, prompt building, and LLM generation.
"""

from typing import Iterator, Optional, Dict, Any, List
from dataclasses import dataclass

from src.retriever import Retriever
from src.llm import LLMGenerator, ConversationMemory
from src.prompt_builder import PromptBuilder
from src.query_preprocessor import QueryPreprocessor


@dataclass
class QueryResponse:
    """Response from a RAG query."""
    answer: str
    sources: List[Dict[str, Any]]
    query: str
    retrieval_scores: List[float]


class QueryService:
    """
    Complete RAG query service.
    
    Orchestrates:
    1. Query embedding
    2. Vector search
    3. Context assembly
    4. LLM generation
    5. Source attribution
    """
    
    def __init__(
        self,
        retriever: Retriever,
        llm_generator: LLMGenerator,
        prompt_builder: PromptBuilder,
        use_conversation_memory: bool = True,
    ):
        """
        Initialize query service.
        
        Args:
            retriever: Retriever instance
            llm_generator: LLM generator instance
            prompt_builder: Prompt builder instance
            use_conversation_memory: Whether to maintain conversation history
        """
        self.retriever = retriever
        self.llm = llm_generator
        self.prompt_builder = prompt_builder
        self.query_preprocessor = QueryPreprocessor()
        
        # Initialize conversation memory if needed
        if use_conversation_memory:
            self.memory = ConversationMemory(max_messages=20)  # Keep more history for better context
            self.memory.set_system_message(self.prompt_builder.build_system_prompt())
        else:
            self.memory = None
    
    def query(
        self,
        question: str,
        top_k: int = 3,
        diversity: bool = True,
        filter_guest: Optional[str] = None,
    ) -> QueryResponse:
        """
        Process a query and generate a response.
        
        Args:
            question: User's question
            top_k: Number of context chunks to retrieve
            diversity: Whether to use diverse retrieval
            filter_guest: Optional guest name filter
            
        Returns:
            QueryResponse with answer and sources
        """
        # 0. Preprocess query with conversation context
        conversation_context = None
        if self.memory:
            conversation_context = self.memory.get_conversation_context()
        
        processed_query = self.query_preprocessor.preprocess(question, conversation_context)
        
        # Use enhanced query for retrieval
        search_query = processed_query.enhanced_query
        
        # Determine guest preference (soft filter) vs hard filter
        prefer_guest = None
        if not filter_guest and processed_query.suggested_guest_filter and processed_query.confidence >= 0.6:
            prefer_guest = processed_query.suggested_guest_filter
        
        # 1. Retrieve relevant context
        if diversity:
            results = self.retriever.retrieve_with_diversity(
                query=search_query,
                top_k=top_k,
                prefer_guest=prefer_guest,
            )
        else:
            results = self.retriever.retrieve(
                query=search_query,
                top_k=top_k,
                filter_guest=filter_guest,
                prefer_guest=prefer_guest,
            )
        
        # 2. Build context and prompt
        context = self.prompt_builder.build_context(results)
        
        if self.memory:
            # Use conversation memory - only store the question, not the full context
            # This keeps conversation history clean and focused
            self.memory.add_user_message(question)
            
            # Build messages with context included only in current turn
            messages = self.memory.get_messages()
            # Inject context into the last user message (current question)
            context_note = f"\n\nHere are 3 relevant moments from the podcast:\n\n{context}"
            messages[-1]["content"] = messages[-1]["content"] + context_note
        else:
            # Standalone query
            system_prompt = self.prompt_builder.build_system_prompt()
            user_prompt = self.prompt_builder.build_user_prompt(question, context)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        
        # 3. Generate response
        answer = self.llm.generate(messages)
        
        # 4. Update conversation memory with response and context
        if self.memory:
            self.memory.add_assistant_message(answer)
            
            # Extract unique guests from results to track conversation context
            guests_in_response = list(set([result.guest for result in results]))
            topics_in_response = []
            
            # Extract topics from episode themes
            for result in results:
                topics_in_response.extend(result.episode_themes)
            topics_in_response = list(set(topics_in_response))[:3]  # Keep top 3 unique topics
            
            # Update conversation context
            self.memory.update_context(guests_in_response, topics_in_response)
        
        # 5. Format sources
        sources = [result.to_dict() for result in results]
        scores = [result.score for result in results]
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            query=question,
            retrieval_scores=scores,
        )
    
    def query_stream(
        self,
        question: str,
        top_k: int = 3,
        diversity: bool = True,
    ) -> Iterator[str]:
        """
        Process a query and stream the response.
        
        Args:
            question: User's question
            top_k: Number of context chunks to retrieve
            diversity: Whether to use diverse retrieval
            
        Yields:
            Response text chunks
        """
        # 0. Preprocess query with conversation context
        conversation_context = None
        if self.memory:
            conversation_context = self.memory.get_conversation_context()
        
        processed_query = self.query_preprocessor.preprocess(question, conversation_context)
        
        # Use enhanced query for retrieval
        search_query = processed_query.enhanced_query
        
        # Determine guest preference (soft filter)
        prefer_guest = None
        if processed_query.suggested_guest_filter and processed_query.confidence >= 0.6:
            prefer_guest = processed_query.suggested_guest_filter
        
        # 1. Retrieve relevant context
        if diversity:
            results = self.retriever.retrieve_with_diversity(
                query=search_query,
                top_k=top_k,
                prefer_guest=prefer_guest,
            )
        else:
            results = self.retriever.retrieve(
                query=search_query,
                top_k=top_k,
                prefer_guest=prefer_guest,
            )
        
        # 2. Build context and prompt
        context = self.prompt_builder.build_context(results)
        
        if self.memory:
            # Use conversation memory - only store the question, not the full context
            self.memory.add_user_message(question)
            
            # Build messages with context included only in current turn
            messages = self.memory.get_messages()
            # Inject context into the last user message (current question)
            context_note = f"\n\nHere are 3 relevant moments from the podcast:\n\n{context}"
            messages[-1]["content"] = messages[-1]["content"] + context_note
        else:
            system_prompt = self.prompt_builder.build_system_prompt()
            user_prompt = self.prompt_builder.build_user_prompt(question, context)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        
        # 3. Stream response
        full_response = []
        for chunk in self.llm.generate_stream(messages):
            full_response.append(chunk)
            yield chunk
        
        # 4. Update conversation memory after streaming completes
        if self.memory:
            self.memory.add_assistant_message("".join(full_response))
            
            # Extract unique guests from results to track conversation context
            guests_in_response = list(set([result.guest for result in results]))
            topics_in_response = []
            
            # Extract topics from episode themes
            for result in results:
                topics_in_response.extend(result.episode_themes)
            topics_in_response = list(set(topics_in_response))[:3]  # Keep top 3 unique topics
            
            # Update conversation context
            self.memory.update_context(guests_in_response, topics_in_response)
    
    def clear_conversation(self):
        """Clear conversation history."""
        if self.memory:
            self.memory.clear()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get current conversation history."""
        if self.memory:
            return self.memory.get_messages()
        return []


def create_query_service(
    collection_name: str = "wtf_podcast",
    storage_path: str = "./qdrant_db",
    provider: str = "groq",
    model: str = None,
    use_conversation_memory: bool = True,
) -> QueryService:
    """
    Factory function to create a fully initialized QueryService.
    
    Args:
        collection_name: Qdrant collection name
        storage_path: Path to Qdrant storage
        provider: LLM provider ("groq" or "openai")
        model: Model name (if None, uses provider default)
        use_conversation_memory: Whether to use conversation memory
        
    Returns:
        Initialized QueryService
    """
    from src.vector_store import VectorStore
    from src.embeddings import EmbeddingGenerator
    
    # Initialize components
    vector_store = VectorStore(
        collection_name=collection_name,
        storage_path=storage_path,
    )
    
    embedding_generator = EmbeddingGenerator()
    
    retriever = Retriever(
        vector_store=vector_store,
        embedding_generator=embedding_generator,
    )
    
    llm_generator = LLMGenerator(provider=provider, model=model)
    
    prompt_builder = PromptBuilder()
    
    # Create service
    service = QueryService(
        retriever=retriever,
        llm_generator=llm_generator,
        prompt_builder=prompt_builder,
        use_conversation_memory=use_conversation_memory,
    )
    
    return service


if __name__ == "__main__":
    # Test query service
    import sys
    
    print("🧪 Testing Query Service\n")
    
    try:
        # Create service
        print("Initializing query service...")
        service = create_query_service()
        
        # Test queries
        test_queries = [
            "What did Sam Altman say about AI?",
            "Tell me about the future of autonomous vehicles",
            "What are the main themes discussed across the podcasts?",
        ]
        
        for query in test_queries:
            print(f"\n{'='*80}")
            print(f"Query: {query}")
            print("="*80)
            
            response = service.query(query, top_k=3)
            
            print(f"\nAnswer:\n{response.answer}")
            print(f"\nSources: {len(response.sources)} chunks used")
            print(f"Retrieval scores: {[f'{s:.3f}' for s in response.retrieval_scores]}")
        
        print("\n" + "="*80)
        print("✓ Query service test complete")
        
    except ValueError as e:
        print(f"⚠️  {e}")
        print("\nTo test the query service, create a .env file with:")
        print("GROQ_API_KEY=your-key-here (FREE at https://console.groq.com)")
        print("OR")
        print("OPENAI_API_KEY=your-key-here")
        sys.exit(1)

