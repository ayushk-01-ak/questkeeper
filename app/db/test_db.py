# app/db/test_db.py
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.db.database import initialize_database
from app.db.characters import (
    create_character,
    get_character,
    get_all_characters,
    update_character_hp,
)
from app.db.inventory import add_item, get_inventory

initialize_database()

# Check if test character already exists before creating
all_chars = get_all_characters()
arjun_exists = any(c["name"] == "Arjun" for c in all_chars)

if not arjun_exists:
    print("Creating character...")
    arjun_id = create_character(
        name="Arjun",
        character_class="Warrior",
        backstory="A wandering swordsman seeking redemption",
    )
    print(f"Created character with id: {arjun_id}")

    print("\nAdding items to inventory...")
    add_item(arjun_id, "Magic Sword", 1)
    add_item(arjun_id, "Health Potion", 3)
else:
    # Use the first Arjun found
    arjun_id = next(c["id"] for c in all_chars if c["name"] == "Arjun")
    print(f"Character already exists with id: {arjun_id}")

# Fetch and display
arjun = get_character(arjun_id)
print(f"\nCharacter: {arjun}")

items = get_inventory(arjun_id)
print("\nInventory:")
for item in items:
    print(f"  {item['item_name']} x{item['quantity']}")

print("\nAll characters:")
for char in get_all_characters():
    print(f"  id:{char['id']} {char['name']} the {char['class']} HP:{char['hp']}")

from app.db.database import initialize_database
from app.db.characters import (
    create_character,
    get_character,
    get_all_characters,
    update_character_hp,
)
from app.db.inventory import add_item, get_inventory

# Initialize tables
initialize_database()

# Create a character
print("Creating character...")
arjun_id = create_character(
    name="Arjun",
    character_class="Warrior",
    backstory="A wandering swordsman seeking redemption",
)
print(f"Created character with id: {arjun_id}")

# Fetch them back
print("\nFetching character...")
arjun = get_character(arjun_id)
print(f"Found: {arjun}")

# Add inventory items
print("\nAdding items to inventory...")
add_item(arjun_id, "Magic Sword", 1)
add_item(arjun_id, "Health Potion", 3)

# Check inventory
print("\nInventory:")
items = get_inventory(arjun_id)
for item in items:
    print(f"  {item['item_name']} x{item['quantity']}")

# Update HP
print("\nArjun takes 15 damage...")
update_character_hp(arjun_id, 85)

# Verify HP changed
arjun_updated = get_character(arjun_id)
print(f"HP is now: {arjun_updated['hp']}")

# List all characters
print("\nAll characters in database:")
all_chars = get_all_characters()
for char in all_chars:
    print(
        f"  {char['name']} the {char['class']} (Level {char['level']}, HP: {char['hp']})"
    )
