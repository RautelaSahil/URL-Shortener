import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


# ------------------ Connection ------------------

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# ------------------ Users ------------------

def create_user(username, password_hash):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
        """
        cursor.execute(query, (username, password_hash))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT id, username, password_hash
        FROM users
        WHERE username = %s
    """
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user


# ------------------ URL Helpers ------------------

def short_code_exists(short):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT 1 FROM link WHERE short = %s LIMIT 1"
    cursor.execute(query, (short,))
    exists = cursor.fetchone() is not None

    cursor.close()
    conn.close()
    return exists


def insert_url_with_name(original, short, link_name, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO link (original, short, link_name, user_id)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (original, short, link_name, user_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_all_urls(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT id, link_name, original, short, dob
        FROM link
        WHERE user_id = %s
        ORDER BY dob DESC
    """
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def delete_url_by_id(url_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        DELETE FROM link
        WHERE id = %s AND user_id = %s
    """
    cursor.execute(query, (url_id, user_id))
    conn.commit()

    cursor.close()
    conn.close()


def get_original(short):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT original FROM link WHERE short = %s"
    cursor.execute(query, (short,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else None
