import streamlit as st
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SerpAPIWrapper

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize components
@st.cache_resource
def setup_ai():
    groq_api_key = os.getenv("GROQ_API_KEY")
    llm = init_chat_model(
        model="llama-3.1-8b-instant",
        model_provider="groq",
        api_key=groq_api_key
    )

    serpapi_key = os.getenv("SERPAPI_API_KEY")
    search = SerpAPIWrapper(serpapi_api_key=serpapi_key)

    return llm, search

def search_and_answer(llm, search, question):
    """Search and get AI response"""
    try:
        search_results = search.run(question)
        prompt = f"Question: {question}\nSearch results: {search_results}\nProvide a clear, helpful answer:"
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {e}"
    
def direct_chat(llm, message):
    """Direct chat without search"""
    try:
        response = llm.invoke(message)
        return response.content
    except Exception as e:
        return f"Error: {e}"
    

# Main app
def main():
    st.title("🤖 AI Assistant")
    st.markdown("Ask me anything! I can search the web for current information or just chat.")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Setup AI components
    llm, search = setup_ai()

    # Sidebar with options
    st.sidebar.title("Settings")
    search_mode = st.sidebar.radio(
        "Response Mode:",
        ["Auto (Smart)", "Always Search", "Chat Only"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Quick Commands:**")
    st.sidebar.markdown("• Weather: 'weather in Tokyo'")
    st.sidebar.markdown("• News: 'latest AI news'")
    st.sidebar.markdown("• Stocks: 'Apple stock price'")
    st.sidebar.markdown("• General: Ask anything!")

    # Chat interface
    st.subheader("Chat")

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**AI:** {msg['content']}")

    # User input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"**You:** {prompt}")
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Decide whether to search based on mode and content
                if search_mode == "Always Search":
                    response = search_and_answer(llm, search, prompt)
                elif search_mode == "Chat Only":
                    response = direct_chat(llm, prompt)
                else:  # Auto mode
                    search_keywords = ["latest", "current", "today", "news", "price", "what is", "who is", "when did"]
                    needs_search = any(keyword in prompt.lower() for keyword in search_keywords)
                    if needs_search:
                        response = search_and_answer(llm, search, prompt)
                    else:
                        response = direct_chat(llm, prompt)

                st.markdown(f"**AI:** {response}")

        # Add AI response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Clear chat button
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    # Show chat history count
    st.sidebar.markdown(f"**Messages:** {len(st.session_state.messages)}")

if __name__ == "__main__":
    main()