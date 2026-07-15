# app/db/characters.py
# All database operations related to characters
# Each function does exactly one thing (single responsibility)

from app.db.database import get_connection
from datetime import datetime


def create_character(name: str, character_class: str, backstory: str = "") -> int:
    """
    Insert a new character into the database.
    Returns the new character's id.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO characters (name, class, backstory)
        VALUES (?, ?, ?)
    """,
        (name, character_class, backstory),
    )
    # Notice the ? placeholders — NEVER put variables directly in SQL strings
    # That causes SQL injection vulnerabilities
    # The (name, character_class, backstory) tuple fills the ? safely

    # Get the id that was automatically assigned
    new_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return new_id


def get_character(character_id: int) -> dict:
    """
    Fetch one character by their id.
    Returns a dictionary or None if not found.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM characters WHERE id = ?
    """,
        (character_id,),
    )
    # Note the trailing comma in (character_id,)
    # This makes it a tuple, which sqlite3 requires

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    # Convert the Row object to a plain dictionary
    return dict(row)


def get_all_characters() -> list:
    """
    Fetch all characters from the database.
    Returns a list of dictionaries.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM characters ORDER BY name")

    rows = cursor.fetchall()
    connection.close()

    # Convert each Row to a dict and return as list
    return [dict(row) for row in rows]


def update_character_hp(character_id: int, new_hp: int) -> None:
    """
    Update a character's HP after combat or healing.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE characters SET hp = ? WHERE id = ?
    """,
        (new_hp, character_id),
    )

    connection.commit()
    connection.close()


def delete_character(character_id: int) -> None:
    """
    Delete a character permanently.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM characters WHERE id = ?", (character_id,))

    connection.commit()
    connection.close()
