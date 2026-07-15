# tests/test_tools.py
# Basic tests to verify core functions work correctly
# These run automatically in CI on every push

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_roll_dice_valid():
    """Valid dice roll should return a number in range."""
    from app.core.tools import roll_dice

    result = roll_dice(20)

    assert result["success"] is True
    assert 1 <= result["result"] <= 20
    assert result["sides"] == 20


def test_roll_dice_invalid():
    """Invalid dice should fail gracefully."""
    from app.core.tools import roll_dice

    result = roll_dice(7)

    assert result["success"] is False
    assert "error" in result


def test_available_tools_exist():
    """All expected tools should be registered."""
    from app.core.tools import AVAILABLE_TOOLS

    assert "roll_dice" in AVAILABLE_TOOLS
    assert "check_inventory" in AVAILABLE_TOOLS
    assert "deal_damage" in AVAILABLE_TOOLS


def test_detect_npc_mira():
    """Mira keywords should be detected correctly."""
    from app.core.npcs import detect_npc

    result = detect_npc("I speak to Mira Thornquist")
    assert result == "mira_thornquist"


def test_detect_npc_none():
    """Non-NPC messages should return None."""
    from app.core.npcs import detect_npc

    result = detect_npc("I walk through the forest")
    assert result is None


def test_detect_tool_attack():
    """Attack keywords should trigger roll_dice."""
    from app.core.agent import detect_tool_from_message

    tool_name, args = detect_tool_from_message("I attack the goblin")
    assert tool_name == "roll_dice"
    assert args["sides"] == 20


def test_detect_tool_damage():
    """Damage keywords should trigger deal_damage with correct amount."""
    from app.core.agent import detect_tool_from_message

    tool_name, args = detect_tool_from_message(
        "The goblin hits me for 15 damage"
    )
    assert tool_name == "deal_damage"
    assert args["amount"] == 15


def test_detect_tool_inventory():
    """Inventory keywords should trigger check_inventory."""
    from app.core.agent import detect_tool_from_message

    tool_name, args = detect_tool_from_message("What am I carrying?")
    assert tool_name == "check_inventory"