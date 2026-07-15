# app/core/agent.py
import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.llm import ask_llm
from app.core.tools import AVAILABLE_TOOLS


TOOLS_DESCRIPTION = """
You have access to tools. Results will be provided as TOOL_RESULT.
When you see a TOOL_RESULT, use that exact information in your narrative.
Never invent dice numbers, HP values, or inventory items.
NEVER describe the player as dead or unconscious unless 
a TOOL_RESULT explicitly says HP reached 0.
"""

DAMAGE_KEYWORDS = [
    "hits me", "hit me", "attacks me", "attack me",
    "damage", "takes damage", "struck", "wounds me",
    "injures me", "hurts me"
]

ATTACK_KEYWORDS = [
    "i attack", "i strike", "i swing", "i slash",
    "i stab", "i shoot", "i cast", "i charge",
    "i hit", "i fight"
]

INVENTORY_KEYWORDS = [
    "inventory", "carrying", "what do i have",
    "my items", "my bag", "my pack", "what's in"
]


def detect_tool_from_message(message: str) -> tuple:
    """
    Scan player message for keywords and decide which tool to call.
    Returns (tool_name, arguments) or (None, None).
    """
    message_lower = message.lower()

    # Check for damage keywords
    if any(keyword in message_lower for keyword in DAMAGE_KEYWORDS):

        # ✅ FIX: Look for number immediately before "damage" word
        # "level 5 spell for 12 damage" → finds 12, not 5
        # "hits me for 20 damage" → finds 20
        damage_match = re.search(r'(\d+)\s*(?:points?\s*of\s*)?damage', message_lower)

        if damage_match:
            amount = int(damage_match.group(1))
        else:
            # Fallback: no "X damage" pattern, try "for X" pattern
            for_match = re.search(r'for\s+(\d+)', message_lower)
            if for_match:
                amount = int(for_match.group(1))
            else:
                # No number found — roll for damage
                return "roll_dice", {"sides": 6}

        return "deal_damage", {"character_id": 1, "amount": amount}

    # Check for player attack
    if any(keyword in message_lower for keyword in ATTACK_KEYWORDS):
        return "roll_dice", {"sides": 20}

    # Check for inventory
    if any(keyword in message_lower for keyword in INVENTORY_KEYWORDS):
        return "check_inventory", {"character_id": 1}

    return None, None


def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    Look up and execute a tool by name.
    """
    if tool_name not in AVAILABLE_TOOLS:
        return f"Error: Tool '{tool_name}' does not exist."

    tool_function = AVAILABLE_TOOLS[tool_name]
    result = tool_function(**arguments)

    if result.get("success"):
        return result["description"]
    else:
        return f"Tool error: {result.get('error', 'Unknown error')}"


def parse_tool_call(text: str):
    """
    Fallback: check if LLM output contains a tool call.
    """
    pattern_with_prefix = r"TOOL_CALL:\s*(\w+)\(([^)]*)\)"
    match = re.search(pattern_with_prefix, text, re.IGNORECASE)

    if match:
        tool_name = match.group(1).lower()
        args_string = match.group(2)
    else:
        tool_names = "|".join(AVAILABLE_TOOLS.keys())
        pattern_no_prefix = rf"({tool_names})\(([^)]*)\)"
        match = re.search(pattern_no_prefix, text, re.IGNORECASE)

        if not match:
            return None

        tool_name = match.group(1).lower()
        args_string = match.group(2)

    arguments = {}
    if args_string.strip():
        for arg in args_string.split(","):
            arg = arg.strip()
            if "=" in arg:
                key, value = arg.split("=", 1)
                key = key.strip()
                value = value.strip()
                try:
                    arguments[key] = int(value)
                except ValueError:
                    try:
                        arguments[key] = float(value)
                    except ValueError:
                        arguments[key] = value.strip("\"'")

    return tool_name, arguments


def run_agent(prompt: str, player_message: str = "", max_steps: int = 3) -> str:
    """
    Two-stage agent:
    Stage 1 — YOUR CODE detects tools from keywords (reliable)
    Stage 2 — LLM narrates using tool results (creative)
    """

    tool_result_context = ""

    # Stage 1: Pre-detection
    if player_message:
        tool_name, arguments = detect_tool_from_message(player_message)

        if tool_name:
            print(f"[Agent] Pre-detected tool: {tool_name}({arguments})")
            tool_result = execute_tool(tool_name, arguments)
            print(f"[Agent] Tool result: {tool_result}")

            tool_result_context = (
                f"\nTOOL_RESULT: {tool_result}\n"
                f"Use this exact result in your narrative. "
                f"Do not invent different numbers.\n"
            )

    # Stage 2: LLM generates narrative
    full_prompt = prompt + tool_result_context

    steps = 0
    while steps < max_steps:
        steps += 1

        llm_response = ask_llm(full_prompt)
        tool_call = parse_tool_call(llm_response)

        if tool_call is None:
            cleaned = re.sub(r"TOOL_CALL:.*\n?", "", llm_response).strip()
            return cleaned

        tool_name, arguments = tool_call
        print(f"[Agent] LLM called tool: {tool_name}({arguments})")
        tool_result = execute_tool(tool_name, arguments)
        print(f"[Agent] Tool result: {tool_result}")

        full_prompt = (
            full_prompt +
            f"\n{llm_response}"
            f"\nTOOL_RESULT: {tool_result}\n"
            f"\nNow give your final narrative. Do NOT call more tools.\n"
            f"Dungeon Master:"
        )

    cleaned = re.sub(r"TOOL_CALL:.*\n?", "", llm_response)
    cleaned = re.sub(r"TOOL_RESULT:.*\n?", "", cleaned).strip()
    return cleaned