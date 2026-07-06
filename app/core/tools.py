# app/core/tools.py
# These are the actual functions Aldric can call during gameplay
# Each function does exactly one thing and returns a clear result

import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.characters import get_character, update_character_hp
from app.db.inventory import get_inventory


def roll_dice(sides: int) -> dict:
    """
    Roll a single die with the given number of sides.

    Args:
        sides: Number of sides (4, 6, 8, 10, 12, 20, 100)

    Returns:
        Dict with the roll result and description
    """
    # Validate sides — only standard dice allowed
    valid_sides = [4, 6, 8, 10, 12, 20, 100]

    if sides not in valid_sides:
        return {
            "success": False,
            "error": f"Invalid dice. Choose from: {valid_sides}"
        }

    result = random.randint(1, sides)

    return {
        "success": True,
        "sides": sides,
        "result": result,
        "description": f"Rolled d{sides}: {result}"
    }


def check_inventory(character_id: int) -> dict:
    """
    Look up what a character is currently carrying.

    Args:
        character_id: The character's database ID

    Returns:
        Dict with character info and inventory list
    """
    # First check if character exists
    character = get_character(character_id)

    if character is None:
        return {
            "success": False,
            "error": f"No character found with id {character_id}"
        }

    # Get their inventory from database
    items = get_inventory(character_id)

    return {
        "success": True,
        "character_name": character["name"],
        "character_class": character["class"],
        "current_hp": character["hp"],
        "inventory": items,    # List of {item_name, quantity} dicts
        "description": f"{character['name']} is carrying: " +
                      (", ".join([f"{i['item_name']} x{i['quantity']}"
                                  for i in items])
                       if items else "nothing")
    }


def deal_damage(character_id: int, amount: int) -> dict:
    """
    Apply damage to a character and update the database.

    Args:
        character_id: The character's database ID
        amount: How much damage to deal (positive number)

    Returns:
        Dict with old HP, new HP, and whether character is down
    """
    character = get_character(character_id)

    if character is None:
        return {
            "success": False,
            "error": f"No character found with id {character_id}"
        }

    old_hp = character["hp"]

    # Calculate new HP — never goes below 0
    new_hp = max(0, old_hp - amount)

    # Update in database permanently
    update_character_hp(character_id, new_hp)

    # Check if character is down
    is_down = new_hp == 0

    return {
        "success": True,
        "character_name": character["name"],
        "old_hp": old_hp,
        "damage_dealt": amount,
        "new_hp": new_hp,
        "is_down": is_down,
        "description": (
            f"{character['name']} took {amount} damage. "
            f"HP: {old_hp} → {new_hp}. "
            f"{'UNCONSCIOUS!' if is_down else 'Still standing.'}"
        )
    }


# Map tool names to actual functions
# This is how we'll look up which function to call later
AVAILABLE_TOOLS = {
    "roll_dice": roll_dice,
    "check_inventory": check_inventory,
    "deal_damage": deal_damage
}


# Test when run directly
if __name__ == "__main__":
    print("Testing tools...\n")

    # Test dice rolling
    print("=== DICE ROLLS ===")
    print(roll_dice(20))
    print(roll_dice(6))
    print(roll_dice(7))  # Invalid — should fail gracefully

    print("\n=== INVENTORY CHECK ===")
    # Uses character id=1 (Arjun from Phase 5 test)
    print(check_inventory(1))

    print("\n=== DEAL DAMAGE ===")
    print(deal_damage(1, 15))

    # Check HP actually changed in database
    from app.db.characters import get_character
    updated = get_character(1)
    print(f"Confirmed new HP in database: {updated['hp']}")