"""
Chat interface components
"""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from audio_recorder_streamlit import audio_recorder
from utils.voice_utils import speech_to_text_whisper, text_to_speech_openai, autoplay_audio, get_available_voices



def render_chat_interface(agent_executor):
    """Render the main chat interface with voice support"""
    
    st.markdown("---")

    # Voice controls header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("💬 Chat")
    with col2:
        voice_enabled = st.toggle("🎤 Voice", value=st.session_state.get("voice_enabled", False))
        st.session_state.voice_enabled = voice_enabled
    with col3:
        if voice_enabled:
            auto_speak = st.toggle("🔊 Auto-Speak", value=st.session_state.get("auto_speak", True))
            st.session_state.auto_speak = auto_speak


    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

        # Add "Read aloud" button for AI responses
        if message["role"] == "assistant" and voice_enabled:
            col_a, col_b = st.columns([6, 1])
            with col_b:
                if st.button("🔊", key=f"tts_{i}", help="Read aloud"):
                    with st.spinner("Generating speech..."):
                        voice = st.session_state.get("selected_voice", "alloy")
                        audio_bytes = text_to_speech_openai(message["content"], voice=voice)
                        if audio_bytes:
                            autoplay_audio(audio_bytes)
    
    # Process pending question from sidebar button
    if st.session_state.pending_question:
        prompt = st.session_state.pending_question
        st.session_state.pending_question = None  # Clear it
        
        # Process the question
        _process_user_input(prompt, agent_executor)
        st.rerun()  # Rerun to show the complete exchange
    
    # Voice input area
    if voice_enabled:
        st.markdown("---")
        col_v1, col_v2 = st.columns([3, 1])

        with col_v1:
            st.markdown("**🎤 Voice Input** - Click the microphone to record your question")

        with col_v2:
            # Voice selection dropdown (compact)
            voices = get_available_voices()

            selected_voice = st.selectbox(
                "Voice",
                options=list(voices.keys()),
                format_func=lambda x: f"{x.title()} - {voices[x]}",
                index=0,
                key="voice_selector",
                label_visibility="collapsed"
            )
            st.session_state.selected_voice = selected_voice

        #Audio recorder
        audio_bytes = audio_recorder(
            text="",
            recording_color="#e74c3c",
            neutral_color="#3498db",
            icon_size="2x",
            key="audio_recorder"
        )

        if audio_bytes:
            # Show audio preview
            with st.expander("🎵 Recording preview", expanded=False):
                st.audio(audio_bytes, format="audio/wav")

            # Transcribe audio to text
            with st.spinner("🎤 Transcribing with Whisper..."):
                transcribed_text = speech_to_text_whisper(audio_bytes)

            if transcribed_text and not transcribed_text.startswith("❌"):
                st.success(f"📝 **You said:** {transcribed_text}")

                # Auto-submit button
                if st.button("✅ Send this message", type="primary", use_container_width=True):
                    auto_speak = st.session_state.get("auto_speak", True)
                    _process_user_input(transcribed_text, agent_executor, auto_speak=auto_speak)
                    st.rerun()  # Rerun to show the complete exchange

            else:
                st.error(transcribed_text)
        
        st.markdown("---")

    # Text input area (always shown)
    if prompt := st.chat_input("Type your message or use voice input above..."):
        auto_speak = voice_enabled and st.session_state.get("auto_speak", False)
        _process_user_input(prompt, agent_executor, auto_speak=auto_speak)

    # Show chat statistics
    _render_chat_stats()


def _process_user_input(prompt: str, agent_executor, auto_speak: bool = False):
    """Process user input and generate AI response"""
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Auto-save user message if enabled
    if st.session_state.get("auto_save_enabled", False):
        if "firestore_manager" in st.session_state:
            firestore_manager = st.session_state.firestore_manager
            session_id = st.session_state.get("session_id", "default")
            firestore_manager.save_message(session_id, "user", prompt)
    
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
                
                # Auto-save assistant message if enabled
                if st.session_state.get("auto_save_enabled", False):
                    if "firestore_manager" in st.session_state:
                        firestore_manager = st.session_state.firestore_manager
                        session_id = st.session_state.get("session_id", "default")
                        firestore_manager.save_message(session_id, "assistant", answer)

                # Atuo-speak the response if enabled
                if auto_speak:
                    with st.spinner("🔊 Generating speech..."):
                        voice = st.session_state.get("selected_voice", "alloy")
                        audio_bytes = text_to_speech_openai(answer, voice=voice)
                        if audio_bytes:
                            autoplay_audio(audio_bytes)
                
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