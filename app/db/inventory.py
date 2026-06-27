# app/db/inventory.py
# Database operations for character inventory

from app.db.database import get_connection


def add_item(character_id: int, item_name: str, quantity: int = 1) -> None:
    """
    Add an item to a character's inventory.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO inventory (character_id, item_name, quantity)
        VALUES (?, ?, ?)
    """, (character_id, item_name, quantity))

    connection.commit()
    connection.close()


def get_inventory(character_id: int) -> list:
    """
    Get all items a character is carrying.
    Returns list of dicts with item_name and quantity.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT item_name, quantity
        FROM inventory
        WHERE character_id = ?
        ORDER BY item_name
    """, (character_id,))

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def remove_item(character_id: int, item_name: str) -> None:
    """
    Remove an item from a character's inventory.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM inventory
        WHERE character_id = ? AND item_name = ?
    """, (character_id, item_name))

    connection.commit()
    connection.close()