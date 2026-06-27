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
    Safe to call multiple times — won't overwrite existing data.
    """
    connection = get_connection()

    # cursor is what actually executes SQL commands
    cursor = connection.cursor()

    # --- Characters Table ---
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
    # INTEGER PRIMARY KEY AUTOINCREMENT → id is assigned automatically
    # NOT NULL → this field must always have a value
    # DEFAULT → what value to use if none is provided

    # --- Sessions Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            started_at   TEXT NOT NULL,
            summary      TEXT DEFAULT '',
            FOREIGN KEY (character_id) REFERENCES characters(id)
        )
    """)
    # FOREIGN KEY links character_id here to id in characters table
    # This enforces that you can't create a session for a non-existent character

    # --- Inventory Table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            item_name    TEXT NOT NULL,
            quantity     INTEGER DEFAULT 1,
            FOREIGN KEY (character_id) REFERENCES characters(id)
        )
    """)

    # Save the changes permanently
    connection.commit()

    # Always close the connection when done
    connection.close()

    print(f"Database initialized at: {DB_PATH}")


# Run initialization when this file is executed directly
if __name__ == "__main__":
    initialize_database()