from flask import Flask, request, jsonify, redirect
from db import insert_url, get_original
import random
import string

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_valid_url(url):
    if not url:
        return False
    return url.startswith("http://") or url.startswith("https://")

app = Flask(__name__)

@app.route("/")
def home():
    return "URL Shortener Backend Running"

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/api/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()

    if not data or "long_url" not in data:
        return jsonify({"error": "long_url is required"}), 400

    long_url = data.get("long_url")

    if not is_valid_url(long_url):
        return jsonify({"error": "Invalid URL"}), 400

    short_code = generate_short_code()
    insert_url(long_url, short_code)

    short_url = f"http://localhost:5000/{short_code}"
    return jsonify({"short_url": short_url}), 200

@app.route("/<short_code>")
def redirect_short_url(short_code):
    original = get_original(short_code)
    if original:
        return redirect(original)
    return "URL not found", 404

if __name__ == "__main__":
    app.run(debug=True)
