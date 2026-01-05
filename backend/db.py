import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def insert_url(original, pipiurl):
    conn= get_connection()
    cursor= conn.cursor()
    
    query= "insert into dmforlink (original, pipiurl) values (%s, %s)"
        
    cursor.execute(query,(original, pipiurl))
    conn.commit()
    cursor.close()
    conn.close()

def get_original(pipiurl):
    conn= get_connection()
    cursor= conn.cursor()
    
    query= "select original from dmforlink where pipiurl= %s"
        
    cursor.execute(query,( pipiurl,))
    
    result= cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if result:
        return result[0]
    return None

