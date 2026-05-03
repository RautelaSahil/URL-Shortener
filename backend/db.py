import sqlite3
import os
import string
import random
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_NAME", "url_shortener.db")

def init_db():
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS link (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original TEXT NOT NULL,
                short TEXT NOT NULL UNIQUE,
                link_name TEXT,
                user_id INTEGER NOT NULL,
                dob TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                click_count INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
    except sqlite3.Error as err:
        logger.critical(f"Failed to initialize SQLite database: {err}", exc_info=True)
        raise RuntimeError(f"Database initialization failed: {err}")
    finally:
        conn.close()

def get_connection():
    try:
        # detect_types ensures DATE/TIMESTAMP columns are parsed into python datetime objects
        conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys constraint enforcement in SQLite
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as err:
        logger.error(f"Failed to get connection to SQLite db: {err}", exc_info=True)
        raise RuntimeError(f"Database connection blocked or failed: {err}")



# ------------------ Users ------------------

def create_user(username, password_hash):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        """
        cursor.execute(query, (username, password_hash))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as err:
        logger.warning(f"Duplicate user registration attempt for username: {username}")
        raise ValueError("Username already exists")
    except sqlite3.Error as err:
        logger.error(f"Database error in create_user: {err}", exc_info=True)
        raise RuntimeError("Failed to create user due to database error")
    finally:
        if conn: conn.close()


def get_user_by_username(username):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT id, username, password_hash
            FROM users
            WHERE username = ?
        """
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as err:
        logger.error(f"Database error in get_user_by_username: {err}", exc_info=True)
        raise RuntimeError("Database error occurred while fetching user")
    finally:
        if conn: conn.close()


def get_username_by_id(user_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as err:
        logger.error(f"Database error in get_username_by_id: {err}", exc_info=True)
        raise RuntimeError("Database error occurred while fetching user ID")
    finally:
        if conn: conn.close()


# ------------------ URL Helpers ------------------


def _generate_short_code(length=6):
    """Generate a random alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def insert_url_with_retry(original, link_name, user_id, max_retries=5):
    """Insert a URL with a randomly generated short code.
    Retries with a new code on duplicate key collision.
    Returns the short code that was successfully inserted.
    Raises RuntimeError if all retries are exhausted or on other DB errors.
    """
    for attempt in range(1, max_retries + 1):
        short = _generate_short_code()
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO link (original, short, link_name, user_id)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, (original, short, link_name, user_id))
            conn.commit()
            return short
        except sqlite3.IntegrityError as err:
            logger.warning(f"Short code collision on attempt {attempt}/{max_retries}: {short}")
            continue
        except sqlite3.Error as err:
            logger.error(f"Database error in insert_url_with_retry: {err}", exc_info=True)
            raise RuntimeError("Database error during insert")
        finally:
            if conn: conn.close()

    logger.error(f"Short code generation exhausted after {max_retries} retries")
    raise RuntimeError("Failed to generate a unique short code. Please try again.")


def insert_url_custom_code(original, short, link_name, user_id):
    """Insert a URL with a user-provided custom short code.
    Raises ValueError if the code already exists.
    Raises RuntimeError on other DB errors.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO link (original, short, link_name, user_id)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (original, short, link_name, user_id))
        conn.commit()
    except sqlite3.IntegrityError as err:
        logger.warning(f"Custom short code already exists: {short}")
        raise ValueError("Custom short code already exists")
    except sqlite3.Error as err:
        logger.error(f"Database error in insert_url_custom_code: {err}", exc_info=True)
        raise RuntimeError("Database error during insert")
    finally:
        if conn: conn.close()


def update_link_name(short_code, link_name):
    """Update the link_name for a row after background scraping completes."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE link SET link_name = ? WHERE short = ?",
            (link_name, short_code)
        )
        conn.commit()
    except sqlite3.Error as err:
        logger.error(f"Database error in update_link_name for {short_code}: {err}", exc_info=True)
        raise RuntimeError("Database error while updating link name")
    finally:
        if conn: conn.close()


def get_all_urls(user_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT id, link_name, original, short, dob as "dob [timestamp]", click_count
            FROM link
            WHERE user_id = ?
            ORDER BY dob DESC
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    except sqlite3.Error as err:
        logger.error(f"Database error in get_all_urls: {err}", exc_info=True)
        raise RuntimeError("Database error while fetching URLs")
    finally:
        if conn: conn.close()


def delete_url_by_id(url_id, user_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            DELETE FROM link
            WHERE id = ? AND user_id = ?
        """
        cursor.execute(query, (url_id, user_id))
        conn.commit()
    except sqlite3.Error as err:
        logger.error(f"Database error in delete_url_by_id: {err}", exc_info=True)
        raise RuntimeError("Database error while deleting URL")
    finally:
        if conn: conn.close()


def get_original_and_increment(short):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        select_query = "SELECT original FROM link WHERE short = ?"
        cursor.execute(select_query, (short,))
        result = cursor.fetchone()

        if not result:
            return None

        original_url = result['original']

        update_query = """
            UPDATE link
            SET click_count = click_count + 1
            WHERE short = ?
        """
        cursor.execute(update_query, (short,))
        conn.commit()

        return original_url
    except sqlite3.Error as err:
        logger.error(f"Database error in get_original_and_increment: {err}", exc_info=True)
        raise RuntimeError("Database error resolving redirect")
    finally:
        if conn: conn.close()


# ------------------ Stats ------------------

def get_user_stats(user_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                COUNT(*) AS total_links,
                COALESCE(SUM(click_count), 0) AS total_clicks
            FROM link
            WHERE user_id = ?
        """
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else {"total_links": 0, "total_clicks": 0}
    except sqlite3.Error as err:
        logger.error(f"Database error in get_user_stats: {err}", exc_info=True)
        raise RuntimeError("Database error while fetching stats")
    finally:
        if conn: conn.close()
