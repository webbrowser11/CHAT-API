import json
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory message store, keyed by message id (auto increment)
messages_store = {
    "messages": [],
    "last_id": 0
}

def is_valid_message(msg):
    return (
        "user" in msg and isinstance(msg["user"], str) and
        "text" in msg and isinstance(msg["text"], str) and
        ("timestamp" not in msg or isinstance(msg["timestamp"], (int, float)))
    )

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <head>
        <title>Friend Chat API</title>
    </head>
    <body>
        <h1>Friend Chat API</h1>
        <p>Use GET /messages to fetch chat messages.</p>
        <p>Use POST /messages with JSON {user, text, timestamp?} to send messages.</p>
    </body>
    '''

@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(messages_store["messages"])

@app.route('/messages', methods=['POST'])
def post_message():
    try:
        new_message = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    # Accept either a single message or a list of messages
    if isinstance(new_message, list):
        messages_to_add = new_message
    else:
        messages_to_add = [new_message]

    added_messages = []
    for msg in messages_to_add:
        if not is_valid_message(msg):
            return jsonify({"error": "Invalid message format"}), 400

        messages_store["last_id"] += 1
        msg_id = messages_store["last_id"]
        # Use current time if timestamp not provided
        timestamp = msg.get("timestamp", int(time.time()))
        message_obj = {
            "id": msg_id,
            "user": msg["user"],
            "text": msg["text"],
            "timestamp": timestamp
        }
        messages_store["messages"].append(message_obj)
        added_messages.append(message_obj)

    return jsonify({"added": added_messages}), 201

if __name__ == "__main__":
    app.run(port=5000)
