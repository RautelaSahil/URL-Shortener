from flask import Flask, request, jsonify, redirect, render_template, session
from flask_cors import CORS
import random
import string
import requests
from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash, check_password_hash

from .db import (
    short_code_exists,
    insert_url_with_name,
    get_original,
    get_all_urls,
    delete_url_by_id,
    create_user,
    get_user_by_username
)

BASE_URL = "http://127.0.0.1:5000"


app = Flask(__name__)

# ------------------ CORS & SESSION ------------------

CORS(
    app,
    supports_credentials=True,
    origins=["http://127.0.0.1:5500"]

)

app.secret_key = "dev-secret-change-later"

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False
)

# ------------------ Helpers ------------------

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def fetch_link_name(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        if soup.title and soup.title.string:
            return soup.title.string.strip()[:250]
    except Exception:
        pass
    return url.split("//")[-1].split("/")[0]


def is_valid_url(url):
    return url and url.startswith(("http://", "https://"))


def login_required():
    return "user_id" in session


# ------------------ Basic ------------------

@app.route("/")
def home():
    return "Shortly Backend Running"


@app.route("/health")
def health():
    return {"status": "ok"}


# ------------------ Auth ------------------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    try:
        user_id = create_user(username, generate_password_hash(password))
        session.clear()
        session["user_id"] = user_id
        return jsonify({"message": "Registered"}), 201
    except Exception:
        return jsonify({"error": "User already exists"}), 400


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    user = get_user_by_username(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    session.clear()
    session["user_id"] = user["id"]
    return jsonify({"message": "Logged in"}), 200


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200


# ------------------ Core ------------------

@app.route("/api/shorten", methods=["POST"])
def shorten_url():
    if not login_required():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    long_url = data.get("long_url")

    if not is_valid_url(long_url):
        return jsonify({"error": "Invalid URL"}), 400

    short_code = generate_short_code()
    while short_code_exists(short_code):
        short_code = generate_short_code()

    insert_url_with_name(
        long_url,
        short_code,
        fetch_link_name(long_url),
        session["user_id"]
    )

    return jsonify({"short_url": f"{BASE_URL}/{short_code}"}), 200


@app.route("/api/urls", methods=["GET"])
def get_urls():
    if not login_required():
        return jsonify({"error": "Unauthorized"}), 401

    rows = get_all_urls(session["user_id"])
    return jsonify([
        {
            "id": r["id"],
            "link_name": r["link_name"],
            "short_url": f"{BASE_URL}/{r['short']}",
            "original": r["original"],
            "created_at": r["dob"].strftime("%Y-%m-%d %H:%M")
        }
        for r in rows
    ]), 200


@app.route("/api/urls/<int:url_id>", methods=["DELETE"])
def delete_url(url_id):
    if not login_required():
        return jsonify({"error": "Unauthorized"}), 401

    delete_url_by_id(url_id, session["user_id"])
    return "", 204


# ------------------ Redirect ------------------

@app.route("/<short_code>")
def redirect_short_url(short_code):
    original = get_original(short_code)
    if original:
        return redirect(original, code=302)
    return render_template("not_found.html"), 404


# ------------------ Run ------------------

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
