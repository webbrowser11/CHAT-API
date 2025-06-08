import json
import time
import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Environment variables for Upstash Redis REST API
UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

def get_messages():
    """Fetch all messages from Redis"""
    try:
        response = requests.get(
            f"{UPSTASH_REDIS_REST_URL}/lrange/messages/0/-1",
            headers={"Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}"}
        )
        if response.status_code == 200:
            return [json.loads(m) for m in response.json()['result']]
        return []
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []

def save_message(message):
    """Save a new message to Redis"""
    try:
        response = requests.post(
            f"{UPSTASH_REDIS_REST_URL}/rpush/messages",
            headers={"Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}"},
            json={"value": json.dumps(message)}
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error saving message: {e}")
        return False

@app.route('/')
def index():
    return "<h1>SEGAFriends Chat API</h1><p>Use /messages endpoint</p>"

@app.route('/messages', methods=['GET'])
def handle_get_messages():
    """Get all messages"""
    messages = get_messages()
    return jsonify(messages)

@app.route('/messages', methods=['POST'])
def handle_post_message():
    """Post a new message"""
    data = request.get_json()
    
    # Validate input
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request format"}), 400
    
    required_fields = ['user', 'text']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields (user, text)"}), 400
    
    if not isinstance(data['user'], str) or not isinstance(data['text'], str):
        return jsonify({"error": "User and text must be strings"}), 400
    
    if not data['user'].strip() or not data['text'].strip():
        return jsonify({"error": "User and text cannot be empty"}), 400

    # Create message object
    message = {
        "user": data["user"].strip(),
        "text": data["text"].strip(),
        "timestamp": int(time.time() * 1000)  # Using milliseconds for more precision
    }

    # Save to Redis
    if not save_message(message):
        return jsonify({"error": "Failed to save message to database"}), 500

    return jsonify(message), 201

if __name__ == '__main__':
    # Check if required environment variables are set
    if not UPSTASH_REDIS_REST_URL or not UPSTASH_REDIS_REST_TOKEN:
        print("Error: UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN must be set")
        exit(1)
    
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
