from flask import Flask, request, jsonify, redirect, render_template, session, abort
from flask_cors import CORS
import os
import re

from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
logger = logging.getLogger(__name__)

from backend.db import (
    get_username_by_id,
    create_user,
    get_user_by_username,
    get_user_stats,
    init_db
)

from backend.services.url_service import (
    create_short_url,
    get_user_urls_service,
    delete_user_url_service,
    resolve_redirect_service
)

# Initialize schema explicitly
init_db()

# ------------------ CONFIG ------------------

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# ------------------ CORS & SESSION ------------------

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:5501").split(",")

CORS(
    app,
    supports_credentials=True,
    origins=CORS_ORIGINS
)

app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-later")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
)

# ------------------ Helpers ------------------


def login_required():
    return "user_id" in session


# ------------------ Basic Routes ------------------

@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/health")
def health():
    return {"status": "ok"}


@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return app.send_static_file("index.html"), 404


@app.route("/api/check-auth", methods=["GET"])
def check_auth():
    return jsonify({
        "authenticated": "user_id" in session
    }), 200


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
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        logger.error(f"Runtime DB error in register: {e}")
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in register: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    try:
        user = get_user_by_username(username)
        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        session.clear()
        session["user_id"] = user["id"]
        return jsonify({"message": "Logged in"}), 200
    except RuntimeError as e:
        logger.error(f"Runtime DB error in login: {e}")
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in login: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500


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
    custom_code = data.get("custom_code")

    try:
        short_code = create_short_url(long_url, custom_code, session["user_id"])
        return jsonify({"short_url": f"{BASE_URL}/{short_code}"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        logger.error(f"Runtime DB error in shorten_url: {e}")
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in shorten_url: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/urls", methods=["GET"])
def get_urls():
    if not login_required():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        rows = get_user_urls_service(session["user_id"])
        return jsonify([
            {
                "id": r["id"],
                "link_name": r["link_name"],
                "short_url": f"{BASE_URL}/{r['short']}",
                "original": r["original"],
                "click_count": r["click_count"],
                "created_at": r["dob"].strftime("%Y-%m-%d %H:%M")
            }
            for r in rows
        ]), 200
    except RuntimeError as e:
        logger.error(f"Runtime DB error fetching URLs: {e}")
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching URLs: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    if not login_required():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        stats = get_user_stats(session["user_id"])
        user = get_username_by_id(session["user_id"])

        return jsonify({
            "username": user["username"],
            "total_links": stats["total_links"],
            "total_clicks": stats["total_clicks"]
        }), 200
    except RuntimeError as e:
        logger.error(f"Runtime DB error fetching stats: {e}")
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching stats: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route("/api/urls/<int:url_id>", methods=["DELETE"])
def delete_url(url_id):
    if not login_required():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        delete_user_url_service(url_id, session["user_id"])
        return "", 204
    except RuntimeError as e:
        logger.error(f"Runtime DB error deleting URL: {e}")
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        logger.error(f"Unexpected error deleting URL: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500


# ------------------ Redirect ------------------

@app.route("/<short_code>")
def redirect_short_url(short_code):

    # Skip API
    if short_code.startswith("api"):
        abort(404)

    # Skip static files
    if "." in short_code:
        try:
            return app.send_static_file(short_code)
        except Exception:
            abort(404)

    # Validate short code
    if not re.match(r"^[a-zA-Z0-9]{3,10}$", short_code):
        abort(404)

    original = resolve_redirect_service(short_code)

    if original:
        return redirect(original, code=302)

    abort(404)

# ------------------ Run ------------------

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
