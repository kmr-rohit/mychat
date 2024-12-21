from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import secrets
import threading
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# In-memory message storage
messages = []
KEYWORD = "troitroi"  # Change this to your desired secret keyword

def cleanup_messages():
    """Delete messages older than 1 hour"""
    while True:
        current_time = datetime.now()
        global messages
        messages = [msg for msg in messages if 
                   (current_time - msg['timestamp']) < timedelta(minutes=5)]
        time.sleep(60)  # Check every minute

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_messages, daemon=True)
cleanup_thread.start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/join', methods=['POST'])
def join():
    keyword = request.json.get('keyword')
    if keyword == KEYWORD:
        session['authenticated'] = True
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid keyword'}), 401

@app.route('/send', methods=['POST'])
def send_message():
    if not session.get('authenticated'):
        return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
    
    message = request.json.get('message')
    sender = request.json.get('sender')
    
    if message and sender:
        messages.append({
            'sender': sender,
            'message': message,
            'timestamp': datetime.now()
        })
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid message'}), 400

@app.route('/messages')
def get_messages():
    if not session.get('authenticated'):
        return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
    return jsonify(messages)

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # Enable HTTPS