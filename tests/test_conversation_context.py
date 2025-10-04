"""
Test Conversation Context and Speaker Attribution

Tests that the system properly maintains conversation context
and handles speaker attribution correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.query_service import create_query_service


def test_conversation_continuity():
    """
    Test that conversation context is maintained across queries.
    
    Simulates the exact scenario from the bug report:
    1. Ask about securing engineering jobs (Vinod Khosla responds)
    2. Ask "what does sam altman think" (should stay in Khosla context or indicate no Sam content)
    """
    print("🧪 Testing Conversation Context and Speaker Attribution\n")
    print("="*80)
    
    try:
        # Create service with conversation memory enabled
        print("\n1. Initializing query service with conversation memory...")
        service = create_query_service(use_conversation_memory=True)
        print("   ✓ Service initialized")
        
        # Query 1: Ask about securing engineering jobs
        print("\n" + "="*80)
        print("Query 1: 'how can i secure my job as an engineer in the AI future?'")
        print("="*80)
        
        response1 = service.query(
            question="how can i secure my job as an engineer in the AI future?",
            top_k=3,
            diversity=True,
        )
        
        print(f"\nAnswer:\n{response1.answer}\n")
        print(f"Sources: {len(response1.sources)} chunks")
        for i, source in enumerate(response1.sources, 1):
            print(f"  {i}. {source['guest']} (score: {source['score']:.3f})")
        
        # Check conversation context
        if service.memory:
            context = service.memory.get_conversation_context()
            print(f"\nConversation Context:")
            print(f"  Active Guests: {context['active_guests']}")
            print(f"  Recent Topics: {context['recent_topics']}")
        
        # Query 2: Ask about Sam Altman (follow-up)
        print("\n" + "="*80)
        print("Query 2: 'what does sam altman think'")
        print("="*80)
        print("Expected behavior: Should either:")
        print("  a) Stay in Khosla context if no Sam Altman content available, OR")
        print("  b) Find Sam Altman content if it exists, OR")
        print("  c) Indicate no Sam Altman content in these excerpts")
        print()
        
        response2 = service.query(
            question="what does sam altman think",
            top_k=3,
            diversity=True,
        )
        
        print(f"\nAnswer:\n{response2.answer}\n")
        print(f"Sources: {len(response2.sources)} chunks")
        for i, source in enumerate(response2.sources, 1):
            print(f"  {i}. {source['guest']} (score: {source['score']:.3f})")
        
        # Check if we got Bill Gates (the bug!)
        guests_in_response2 = [s['guest'] for s in response2.sources]
        if 'Bill Gates' in guests_in_response2:
            print("\n⚠️  WARNING: Got Bill Gates content when asking about Sam Altman!")
            print("   This is the bug we're trying to fix.")
        
        # Check conversation context
        if service.memory:
            context = service.memory.get_conversation_context()
            print(f"\nConversation Context:")
            print(f"  Active Guests: {context['active_guests']}")
            print(f"  Recent Topics: {context['recent_topics']}")
        
        # Query 3: Test explicit guest mention
        print("\n" + "="*80)
        print("Query 3: 'what does vinod khosla think about AI startups?'")
        print("="*80)
        print("Expected behavior: Should retrieve Vinod Khosla content")
        print()
        
        response3 = service.query(
            question="what does vinod khosla think about AI startups?",
            top_k=3,
            diversity=True,
        )
        
        print(f"\nAnswer:\n{response3.answer}\n")
        print(f"Sources: {len(response3.sources)} chunks")
        for i, source in enumerate(response3.sources, 1):
            print(f"  {i}. {source['guest']} (score: {source['score']:.3f})")
        
        guests_in_response3 = [s['guest'] for s in response3.sources]
        if 'Vinod Khosla' in guests_in_response3:
            print("\n✓ Successfully retrieved Vinod Khosla content")
        else:
            print("\n⚠️  Did not find Vinod Khosla content")
        
        print("\n" + "="*80)
        print("✓ Conversation context test complete")
        print("="*80)
        
    except ValueError as e:
        print(f"\n⚠️  {e}")
        print("\nTo run this test, create a .env file with:")
        print("GROQ_API_KEY=your-key-here (FREE at https://console.groq.com)")
        print("OR")
        print("OPENAI_API_KEY=your-key-here")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_query_preprocessor():
    """Test the query preprocessor directly."""
    print("\n" + "="*80)
    print("Testing Query Preprocessor")
    print("="*80)
    
    from src.query_preprocessor import QueryPreprocessor
    
    preprocessor = QueryPreprocessor()
    
    # Test case 1: Follow-up without context
    result1 = preprocessor.preprocess("what does sam altman think", None)
    print(f"\nTest 1: 'what does sam altman think' (no context)")
    print(f"  Is follow-up: {result1.is_follow_up}")
    print(f"  Detected guest: {result1.detected_guest_mention}")
    print(f"  Suggested filter: {result1.suggested_guest_filter}")
    
    # Test case 2: Follow-up with Khosla context
    context = {
        "active_guests": ["Vinod Khosla"],
        "recent_topics": ["AI jobs", "flexibility"],
        "has_context": True,
    }
    result2 = preprocessor.preprocess("what does sam altman think", context)
    print(f"\nTest 2: 'what does sam altman think' (with Khosla context)")
    print(f"  Is follow-up: {result2.is_follow_up}")
    print(f"  Detected guest: {result2.detected_guest_mention}")
    print(f"  Suggested filter: {result2.suggested_guest_filter}")
    print(f"  Enhanced query: {result2.enhanced_query}")
    
    # Test case 3: Pronoun reference
    result3 = preprocessor.preprocess("what did he say about startups?", context)
    print(f"\nTest 3: 'what did he say about startups?' (with Khosla context)")
    print(f"  Is follow-up: {result3.is_follow_up}")
    print(f"  Suggested filter: {result3.suggested_guest_filter}")
    print(f"  Enhanced query: {result3.enhanced_query}")
    
    print("\n✓ Query preprocessor test complete")


if __name__ == "__main__":
    # Run both tests
    test_query_preprocessor()
    print("\n")
    test_conversation_continuity()

