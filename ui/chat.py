"""
Chat interface components
"""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage



def render_chat_interface(agent_executor):
    """Render the main chat interface"""
    
    st.markdown("---")
    st.subheader("💬 Chat")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Process pending question from sidebar button
    if st.session_state.pending_question:
        prompt = st.session_state.pending_question
        st.session_state.pending_question = None  # Clear it
        
        # Process the question
        _process_user_input(prompt, agent_executor)
        st.rerun()  # Rerun to show the complete exchange
    
    # User input
    if prompt := st.chat_input("Ask me anything..."):
        _process_user_input(prompt, agent_executor)
    
    # Show chat statistics
    _render_chat_stats()


def _process_user_input(prompt: str, agent_executor):
    """Process user input and generate AI response"""
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate AI response using agent
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking and using tools..."):
            try:
                # Build chat history for agent (last 5 exchanges for context)
                agent_chat_history = []
                recent_messages = st.session_state.messages[-10:]  # Last 10 messages (5 exchanges)

                for msg in recent_messages[:-1]:  # Exclude the current message
                    if msg["role"] == "user":
                        agent_chat_history.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        agent_chat_history.append(AIMessage(content=msg["content"]))


                # Invoke the agent with input and chat history
                response = agent_executor.invoke({
                    "input": prompt,
                    "chat_history": agent_chat_history
                    })
                answer = response["output"]
                
                st.markdown(answer)
                
                # Add assistant response to chat
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                error_msg = f"I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})


def _render_chat_stats():
    """Render chat statistics at the bottom"""
    
    if st.session_state.messages:
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        total_messages = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        ai_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        docs_uploaded = len(st.session_state.uploaded_files_names)
        
        with col1:
            st.metric("Total Messages", total_messages)
        with col2:
            st.metric("Your Messages", user_messages)
        with col3:
            st.metric("AI Responses", ai_messages)
        with col4:
            st.metric("📄 Documents", docs_uploaded)