# File: /content_automation/content_system/storage.py

import sqlite3

# Database configuration is kept within its relevant module
DB_FILE = "articles.db"

def article_storage_manager(title: str, content: str, topic: str):
    """Saves the processed content into a SQLite3 database."""
    if not title or not content:
        print("Skipping storage due to empty title or content.")
        return

    try:
        # The DB file will be created in the root directory where main.py is run
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            topic TEXT,
            published_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("INSERT INTO articles (title, content, topic) VALUES (?, ?, ?)", (title, content, topic))

        conn.commit()
        print(f"Successfully saved article: '{title}'")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()