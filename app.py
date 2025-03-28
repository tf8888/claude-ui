import os
import base64
import mimetypes
import uuid
from flask import Flask, render_template, request, jsonify, session
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24).hex())  # Add a secret key for sessions

# Get API key from environment variable
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Store active conversations (in memory for simplicity)
conversations = {}

@app.route('/')
def index():
    # Create new conversation ID if it doesn't exist
    if 'conversation_id' not in session:
        session['conversation_id'] = str(uuid.uuid4())
        conversations[session['conversation_id']] = []
        
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query_claude():
    # Check if API key is available
    api_key = ANTHROPIC_API_KEY
    if not api_key:
        return jsonify({"error": "Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable."}), 400
    
    # Get conversation ID from session
    conversation_id = session.get('conversation_id')
    if not conversation_id or conversation_id not in conversations:
        conversation_id = str(uuid.uuid4())
        session['conversation_id'] = conversation_id
        conversations[conversation_id] = []
    
    # Get query text from form
    query_text = request.form.get('query', '')
    if not query_text:
        return jsonify({"error": "Query text is required"}), 400
    
    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)
    
    # Prepare message content
    message_content = [{"type": "text", "text": query_text}]
    
    # Process uploaded files (if any)
    files = request.files.getlist('files')
    file_contents = []
    
    for file in files:
        if file.filename:
            # Guess content type based on file extension
            content_type, _ = mimetypes.guess_type(file.filename)
            if not content_type:
                content_type = "application/octet-stream"
            
            # Read file data
            file_data = file.read()
            
            # Create base64 encoded data
            base64_data = base64.b64encode(file_data).decode('utf-8')
            
            # Create file content object
            file_content = {
                "type": "document",
                "source": {
                    "type": "base64", 
                    "media_type": content_type, 
                    "data": base64_data
                }
            }
            file_contents.append(file_content)
    
    # If there are files, add them to the message
    if file_contents:
        message_content = file_contents + message_content
    
    # Add user message to conversation history
    conversations[conversation_id].append({
        "role": "user",
        "content": message_content
    })
    
    try:
        # Prepare messages for the API call - this is the key fix
        api_messages = []
        for msg in conversations[conversation_id]:
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Make the API call to Claude with conversation history
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=4000,
            messages=api_messages
        )
        
        # Add assistant response to conversation history
        assistant_message = {
            "role": "assistant",
            "content": [{"type": "text", "text": response.content[0].text}]
        }
        conversations[conversation_id].append(assistant_message)
        
        # Return the response and conversation history
        return jsonify({
            "response": response.content[0].text,
            "conversation": [
                {"role": msg["role"], 
                 "content": (msg["content"][0]["text"] if isinstance(msg["content"], list) and 
                             len(msg["content"]) > 0 and 
                             "text" in msg["content"][0] else "(File uploaded)")} 
                for msg in conversations[conversation_id]
            ],
            "files_processed": len(file_contents)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/new_chat', methods=['POST'])
def new_chat():
    # Create a new conversation
    conversation_id = str(uuid.uuid4())
    session['conversation_id'] = conversation_id
    conversations[conversation_id] = []
    return jsonify({"status": "success", "conversation_id": conversation_id})

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    # Clear the current conversation
    conversation_id = session.get('conversation_id')
    if conversation_id and conversation_id in conversations:
        conversations[conversation_id] = []
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
