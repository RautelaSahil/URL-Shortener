import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# ------------------ Connection ------------------

def get_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except mysql.connector.Error as err:
        raise Exception(f"Database connection failed: {err}")


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
    try:
        query = """
            SELECT id, username, password_hash
            FROM users
            WHERE username = %s
        """
        cursor.execute(query, (username,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_username_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


# ------------------ URL Helpers ------------------

def short_code_exists(short):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT 1 FROM link WHERE short = %s LIMIT 1"
        cursor.execute(query, (short,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()


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
    try:
        query = """
            SELECT id, link_name, original, short, dob, click_count
            FROM link
            WHERE user_id = %s
            ORDER BY dob DESC
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def delete_url_by_id(url_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            DELETE FROM link
            WHERE id = %s AND user_id = %s
        """
        cursor.execute(query, (url_id, user_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_original_and_increment(short):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        select_query = "SELECT original FROM link WHERE short = %s"
        cursor.execute(select_query, (short,))
        result = cursor.fetchone()

        if not result:
            return None

        original_url = result[0]

        update_query = """
            UPDATE link
            SET click_count = click_count + 1
            WHERE short = %s
        """
        cursor.execute(update_query, (short,))
        conn.commit()

        return original_url
    finally:
        cursor.close()
        conn.close()


# ------------------ Stats ------------------

def get_user_stats(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                COUNT(*) AS total_links,
                COALESCE(SUM(click_count), 0) AS total_clicks
            FROM link
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
