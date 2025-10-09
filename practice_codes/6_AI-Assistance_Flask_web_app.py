from flask import Flask, app, render_template, request, jsonify
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SerpAPIWrapper

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"

app = Flask(__name__)

# Setup AI components
groq_api_key = os.getenv("GROQ_API_KEY")
llm = init_chat_model(
    model="llama-3.1-8b-instant",
    model_provider="groq",
    api_key=groq_api_key
)

serpapi_key = os.getenv("SERPAPI_API_KEY")
search = SerpAPIWrapper(serpapi_api_key=serpapi_key)

def get_ai_response(message):
    """Get AI response with smart search detection"""
    search_keywords = ["latest", "current", "today", "news", "weather", "price", "what is", "who is", "when is", "where is",
                       "how to", "define", "meaning of", "tell me about", "find", "look up", "search for", "information on"
                       "stock", "quote", "temperature", "forecast", "headlines", "updates", "events", "happening", "trending",
                       "in the world", "in the us", "in my area", "near me", "nearby", "around me", "today's", "this week", "this month",
                       "this year", "recent", "recently", "breaking", "breaking news", "live", "live updates", "live news",
                       "weather report", "weather forecast", "weather today", "weather now", "current weather", "current temperature",
                       "stock price", "stock quote", "stock market", "stock update", "stock information", "stock news"]
    needs_search = any(keyword in message.lower() for keyword in search_keywords)
    
    try:
        if needs_search:
            search_results = search.run(message)
            prompt = f"Question: {message}\nSearch results: {search_results}\nProvide a clear answer:"
            response = llm.invoke(prompt)
            return response.content
        else:
            response = llm.invoke(message)
            return response.content
    except Exception as e:
        return f"Error: {e}"
    
@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 20px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user-message { background-color: #e3f2fd; text-align: right; }
        .ai-message { background-color: #f5f5f5; }
        .input-container { display: flex; }
        #messageInput { flex: 1; padding: 10px; font-size: 16px; }
        #sendButton { padding: 10px 20px; background-color: #2196F3; color: white; border: none; cursor: pointer; }
        #sendButton:hover { background-color: #0b7dda; }
        .loading { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <h1>🤖 AI Assistant</h1>
    <div class="chat-container" id="chatContainer">
        <div class="message ai-message">
            <strong>AI:</strong> Hello! I can help you with questions, search the web for current information, or just chat. What would you like to know?
        </div>
    </div>
    
    <div class="input-container">
        <input type="text" id="messageInput" placeholder="Ask me anything..." onkeypress="handleKeyPress(event)">
        <button id="sendButton" onclick="sendMessage()">Send</button>
    </div>

    <script>
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addMessageToChat('user', message);
            input.value = '';
            
            // Show loading
            const loadingDiv = addMessageToChat('ai', 'Thinking...', true);
            
            try {
                // Send to backend
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                // Remove loading message
                loadingDiv.remove();
                
                // Add AI response
                addMessageToChat('ai', data.response);
                
            } catch (error) {
                loadingDiv.innerHTML = '<strong>AI:</strong> Sorry, there was an error processing your request.';
            }
        }

        function addMessageToChat(sender, message, isLoading = false) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            
            if (sender === 'user') {
                messageDiv.className = 'message user-message';
                messageDiv.innerHTML = `<strong>You:</strong> ${message}`;
            } else {
                messageDiv.className = 'message ai-message' + (isLoading ? ' loading' : '');
                messageDiv.innerHTML = `<strong>AI:</strong> ${message}`;
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            return messageDiv;
        }
    </script>
</body>
</html>
'''

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"response": "Please enter a message."})
    ai_response = get_ai_response(user_message)
    return jsonify({"response": ai_response})

if __name__ == "__main__":
    app.run(debug=True)