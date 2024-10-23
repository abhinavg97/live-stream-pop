import os
import time
from flask import Flask, send_from_directory, Response, render_template
from flask_cors import CORS  # Import Flask-CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

cache = {}


@app.route('/<path:filename>')
def stream_hls(filename):
    """Serve HLS playlist and segments."""

    if filename in cache:
        # cache the file corresponding to {filename} in in-memory cache
        print(f"cache hit for {filename}")
        return cache[filename]

    r = requests.get(f'http://localhost:8001/{filename}')
    cache[filename] = Response(r.content, status=r.status_code, content_type=r.headers['Content-Type'])
    print(f"length of cache now is {len(cache)}")
    return cache[filename]


@app.route('/stream')
def get_chunk():
    """Serve the dynamically updated HLS master playlist with looping."""

    # we can avoid hitting the origin for the HLS files by caching th HLS file response in the PoP server
    # and serving clients with nearby timestamps the same file
    # (time wise bucketing to respond to the clients with HLS file)
    r = requests.get('http://localhost:8001/stream')
    return Response(r.content, status=r.status_code, content_type=r.headers['Content-Type'])

if __name__ == '__main__':
    app.run(debug=True, port=8002)