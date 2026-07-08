# app/db/database.py
# Handles all database connections and table creation
# This is the foundation everything else builds on

import sqlite3
import os

# The database file will be created in the project root
# If it doesn't exist, SQLite creates it automatically
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "questkeeper.db"
)


def get_connection():
    """
    Create and return a database connection.
    
    We call this every time we need to talk to the database.
    Always close the connection when done — like closing a file.
    """
    connection = sqlite3.connect(DB_PATH)

    # This makes rows behave like dictionaries
    # Instead of row[0], row[1] we can do row["name"], row["class"]
    # Much more readable
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create all tables if they don't already exist.
    Safe to call multiple times.
    """
    connection = get_connection()
    cursor = connection.cursor()

    # Characters table (unchanged from Phase 5)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            class     TEXT NOT NULL,
            level     INTEGER DEFAULT 1,
            hp        INTEGER DEFAULT 100,
            backstory TEXT DEFAULT ''
        )
    """)

    # Sessions table — one row per play session
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            started_at   TEXT NOT NULL,
            summary      TEXT DEFAULT '',
            FOREIGN KEY (character_id) REFERENCES characters(id)
        )
    """)

    # Messages table — every single conversation turn
    # This is new in Phase 8
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id   INTEGER NOT NULL,
            character_id INTEGER NOT NULL,
            role         TEXT NOT NULL,
            content      TEXT NOT NULL,
            created_at   TEXT NOT NULL,
            FOREIGN KEY (session_id)   REFERENCES sessions(id),
            FOREIGN KEY (character_id) REFERENCES characters(id)
        )
    """)

    # Inventory table (unchanged from Phase 5)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            item_name    TEXT NOT NULL,
            quantity     INTEGER DEFAULT 1,
            FOREIGN KEY (character_id) REFERENCES characters(id)
        )
    """)

    connection.commit()
    connection.close()
    print(f"Database initialized at: {DB_PATH}")


if __name__ == "__main__":
    initialize_database()