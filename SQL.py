import sqlite3
import os

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)
DB_PATH = os.path.join(
    BASE_DIR,
    "users.db"
)

def connect_db():
    connection = sqlite3.connect(
        DB_PATH
    )

    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            port TEXT NOT NULL
        )
    """)

    connection.commit()
    return connection


def save_user(ip, port):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM connections
        WHERE ip = ? AND port = ?
    """, (
        ip,
        str(port)
    ))
    user = cursor.fetchone()

    if not user:
        cursor.execute("""
            INSERT INTO connections
            (ip, port)
            VALUES (?, ?)
        """, (
            ip,
            str(port)
        ))

    connection.commit()
    connection.close()


def get_users():
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT ip, port
        FROM connections
        ORDER BY id DESC
    """)

    users = cursor.fetchall()
    connection.close()

    return users