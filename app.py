import json
import time
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
UPSTASH_REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN")

app = Flask(__name__)
CORS(app)

def get_messages():
    response = requests.post(
        f"{UPSTASH_REST_URL}/lrange/messages/0/-1",
        headers={"Authorization": f"Bearer {UPSTASH_REST_TOKEN}"}
    )
    if response.status_code == 200:
        return [json.loads(m) for m in response.json()['result']]
    return []

def save_message(message):
    return requests.post(
        f"{UPSTASH_REST_URL}/rpush/messages",
        headers={"Authorization": f"Bearer {UPSTASH_REST_TOKEN}"},
        json={"value": json.dumps(message)}
    )

@app.route('/')
def index():
    return "<h1>Upstash Chat API</h1><p>Use /messages</p>"

@app.route('/messages', methods=['GET'])
def handle_get_messages():
    return jsonify(get_messages())

@app.route('/messages', methods=['POST'])
def handle_post_message():
    data = request.get_json()
    if not data or not isinstance(data, dict) or 'user' not in data or 'text' not in data:
        return jsonify({"error": "Invalid message format"}), 400

    message = {
        "id": int(time.time() * 1000),
        "user": data["user"],
        "text": data["text"],
        "timestamp": int(time.time())
    }

    save_response = save_message(message)
    if save_response.status_code != 200:
        return jsonify({"error": "Failed to save message"}), 500

    return jsonify({"message": message}), 201

if __name__ == '__main__':
    app.run()
