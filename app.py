import os
import random
import time
from prometheus_client import Counter, generate_latest, Gauge
from flask import Flask, send_from_directory, Response, render_template, redirect, url_for
from flask_cors import CORS  # Import Flask-CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Explicitly allow all origins
# Create a counter to track requests
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests (RPS)', ['method', 'endpoint'])

cache = {}
cache_hits, cache_misses = 0, 0


def random_sleep(min_seconds=0, max_seconds=2):
    """
    Pauses execution for a random duration between min_seconds and max_seconds.

    Args:
        min_seconds (float): Minimum sleep duration in seconds (default is 0).
        max_seconds (float): Maximum sleep duration in seconds (default is 2).
    """
    sleep_duration = random.uniform(min_seconds, max_seconds)
    print(f"Sleeping for {sleep_duration:.2f} seconds...")
    time.sleep(sleep_duration)
    print("Done sleeping!")


@app.route('/<path:filename>')
def stream_hls(filename):
    """Serve HLS playlist and segments."""
    REQUEST_COUNT.labels(method='GET', endpoint='/chunk_file').inc()  # Increment request counter
    global cache_hits, cache_misses
    random_sleep()

    if filename in cache:
        cache_hits += 1
        # cache the file corresponding to {filename} in in-memory cache
        print(f"cache hits: {cache_hits}, cache_misses: {cache_misses},"
              f" percentage of hits: {(cache_hits * 100) / (cache_hits + cache_misses)}")
        return cache[filename]

    cache_misses += 1
    r = requests.get(f'http://localhost:8001/{filename}')
    cache[filename] = Response(r.content, status=r.status_code, content_type=r.headers['Content-Type'])

    print(f"cache hits: {cache_hits}, cache_misses: {cache_misses},"
          f" percentage of hits: {(cache_hits*100)/(cache_hits + cache_misses)}")
    return cache[filename]


@app.route('/stream')
def get_chunk():
    REQUEST_COUNT.labels(method='GET', endpoint='/stream').inc()  # Increment request counter
    """Serve the dynamically updated HLS master playlist with looping."""

    # we can avoid hitting the origin for the HLS files by caching th HLS file response in the PoP server
    # and serving clients with nearby timestamps the same file
    # (time wise bucketing to respond to the clients with HLS file)
    r = requests.get('http://localhost:8001/stream')
    return Response(r.content, status=r.status_code, content_type=r.headers['Content-Type'])


@app.route('/metrics', methods=['GET'])
def metrics():
    # Expose Prometheus metrics
    return Response(generate_latest(), mimetype="text/plain")


@app.route('/')
def home():
    # Redirect to the /stream endpoint
    return "Health check succeeded !"


if __name__ == '__main__':
    app.run(debug=True, port=8002, threaded=True)