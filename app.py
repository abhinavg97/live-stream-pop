import os
import time
from flask import Flask, send_from_directory, Response, render_template
from flask_cors import CORS  # Import Flask-CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/<path:filename>')
def stream_hls(filename):
    """Serve HLS playlist and segments."""
    r = requests.get(f'http://localhost:8001/{filename}')
    return Response(r.content, status=r.status_code, content_type=r.headers['Content-Type'])

@app.route('/stream')
def get_chunk():
    """Serve the dynamically updated HLS master playlist with looping."""
    r = requests.get('http://localhost:8001/stream')
    return Response(r.content, status=r.status_code, content_type=r.headers['Content-Type'])

if __name__ == '__main__':
    app.run(debug=True, port=8002)