"""
WTF Podcast RAG - Streamlit Chat Interface

A playful, bold chat interface inspired by AllThingsWTF.com aesthetic.
Colors: Hot Pink (#E91E8C), Golden Yellow (#F2A900), Teal (#4D8B92), Cream (#F5F1E8)
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from src/
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from typing import List, Dict
import time

from src.query_service import create_query_service
from src.retriever import RetrievalResult


# Page configuration
st.set_page_config(
    page_title="WTF Podcast Chat",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - WTF Aesthetic
st.markdown("""
<style>
    /* Import a bold, fun font */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    
    /* Main background */
    .stApp {
        background-color: #F5F1E8;
    }
    
    /* Override default fonts */
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif !important;
    }
    
    /* Main header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #E91E8C;
        text-shadow: 3px 3px 0px #000;
        letter-spacing: -2px;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #4D8B92;
        font-weight: 600;
        margin-bottom: 2rem;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: white !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.15) !important;
        border: 2px solid #000 !important;
    }
    
    /* User messages - Hot Pink */
    [data-testid="stChatMessage"]:has(div[data-testid="stMarkdownContainer"]) {
        background: linear-gradient(135deg, #E91E8C 0%, #F2A900 100%) !important;
    }
    
    /* Source cards */
    .source-card {
        padding: 1.2rem;
        background: linear-gradient(135deg, #F2A900 0%, #4D8B92 100%);
        margin: 1rem 0;
        border-radius: 15px;
        border: 3px solid #000;
        box-shadow: 5px 5px 0px rgba(0, 0, 0, 0.2);
        color: white;
    }
    
    .guest-name {
        font-weight: 700;
        font-size: 1.3rem;
        color: #fff;
        text-shadow: 2px 2px 0px rgba(0, 0, 0, 0.3);
    }
    
    .score-badge {
        background-color: #E91E8C;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 700;
        border: 2px solid #000;
        box-shadow: 2px 2px 0px #000;
    }
    
    /* Input box */
    .stChatInputContainer {
        border: 3px solid #000 !important;
        border-radius: 25px !important;
        background-color: white !important;
        box-shadow: 5px 5px 0px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #E91E8C 0%, #F2A900 100%) !important;
        color: white !important;
        border: 3px solid #000 !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        padding: 0.7rem 1.5rem !important;
        box-shadow: 4px 4px 0px #000 !important;
        transition: all 0.2s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton > button:hover {
        transform: translate(2px, 2px) !important;
        box-shadow: 2px 2px 0px #000 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #4D8B92 !important;
        border-right: 4px solid #000 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.2) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        border: 2px solid rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Decorative elements */
    .emoji-decoration {
        font-size: 2rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Success message */
    .stSuccess {
        background-color: #F2A900 !important;
        color: #000 !important;
        border: 3px solid #000 !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_service():
    """Initialize the query service (cached for performance)."""
    return create_query_service(
        provider="groq",
        model="llama-3.3-70b-versatile",
        use_conversation_memory=True
    )


def format_sources(sources: List[Dict], scores: List[float]) -> str:
    """Format source citations as HTML."""
    html = "<div style='margin-top: 1.5rem;'>"
    html += "<h4>📚 Sources</h4>"
    
    for idx, (source, score) in enumerate(zip(sources, scores), 1):
        guest = source.get('guest', 'Unknown')
        expertise = source.get('guest_expertise', '')
        url = source.get('youtube_url', '#')
        text_preview = source.get('text', '')[:150] + "..."
        
        html += f"""
        <div class='source-card'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span class='guest-name'>{idx}. {guest}</span>
                <span class='score-badge'>Relevance: {score:.1%}</span>
            </div>
            <div style='font-size: 0.9rem; color: #666; margin: 0.3rem 0;'>{expertise}</div>
            <div style='font-size: 0.85rem; color: #888; font-style: italic; margin: 0.5rem 0;'>
                "{text_preview}"
            </div>
            <a href='{url}' target='_blank' style='font-size: 0.9rem;'>🎥 Watch Episode</a>
        </div>
        """
    
    html += "</div>"
    return html


def main():
    """Main application."""
    
    # Header
    st.markdown("<h1 class='main-header'>🎙️ WTF Podcast Chat</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>Ask questions about podcast episodes with Nikhil Kamath's guests</p>",
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model selection
        provider = st.selectbox(
            "LLM Provider",
            ["groq", "openai"],
            index=0,
            help="Groq is free and fast! OpenAI requires API key."
        )
        
        # Number of sources
        top_k = st.slider(
            "Number of sources",
            min_value=3,
            max_value=8,
            value=5,
            help="How many podcast excerpts to retrieve"
        )
        
        # Diversity toggle
        use_diversity = st.checkbox(
            "Diverse sources",
            value=True,
            help="Ensure results come from multiple episodes"
        )
        
        st.divider()
        
        # Stats
        st.header("📊 Stats")
        st.metric("Episodes Loaded", "6")
        st.metric("Total Chunks", "210")
        st.metric("LLM Model", "Llama 3.3 70B")
        
        st.divider()
        
        # Example queries
        st.header("💡 Try asking:")
        example_queries = [
            "What did Sam Altman say about AI?",
            "Tell me about Uber's strategy in India",
            "What are the perspectives on autonomous vehicles?",
            "How do tech leaders think about innovation?",
            "What advice did guests give about entrepreneurship?",
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{query}", use_container_width=True):
                st.session_state.example_query = query
        
        st.divider()
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.service.clear_conversation()
            st.rerun()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "service" not in st.session_state:
        with st.spinner("🔧 Initializing RAG system..."):
            try:
                st.session_state.service = initialize_service()
                st.success("✅ System ready!", icon="🎉")
                time.sleep(0.5)
            except Exception as e:
                st.error(f"❌ Error initializing system: {e}")
                st.info("💡 Make sure you have GROQ_API_KEY in your .env file!")
                st.stop()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if available
            if message["role"] == "assistant" and "sources" in message:
                st.markdown(message["sources"], unsafe_allow_html=True)
    
    # Handle example query from sidebar
    if "example_query" in st.session_state:
        query = st.session_state.example_query
        del st.session_state.example_query
        
        # Process the query
        process_query(query, top_k, use_diversity)
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the podcast episodes..."):
        process_query(prompt, top_k, use_diversity)
        st.rerun()


def process_query(prompt: str, top_k: int, use_diversity: bool):
    """Process a user query and generate response."""
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        sources_placeholder = st.empty()
        
        # Show thinking indicator
        with st.spinner("🤔 Thinking..."):
            try:
                # Query the service (streaming)
                full_response = ""
                
                # Use streaming for better UX
                for chunk in st.session_state.service.query_stream(
                    question=prompt,
                    top_k=top_k,
                    diversity=use_diversity
                ):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                
                # Final response without cursor
                message_placeholder.markdown(full_response)
                
                # Get sources (we need to run query again to get sources - optimization opportunity)
                response = st.session_state.service.query(
                    question=prompt,
                    top_k=top_k,
                    diversity=use_diversity
                )
                
                # Format and display sources
                sources_html = format_sources(response.sources, response.retrieval_scores)
                sources_placeholder.markdown(sources_html, unsafe_allow_html=True)
                
                # Save to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "sources": sources_html
                })
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })


if __name__ == "__main__":
    main()

