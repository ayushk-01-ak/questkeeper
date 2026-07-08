# app/core/agent.py
# The agent loop - bridges the LLM and our tools
# Detects tool calls in LLM output and executes them

import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.llm import ask_llm
from app.core.tools import AVAILABLE_TOOLS


TOOLS_DESCRIPTION = """
IMPORTANT: You have tools available. Use them in the right situations.

FORMAT (use exactly this, one tool per response):
TOOL_CALL: tool_name(arg1=value1, arg2=value2)

TOOLS:

1. TOOL_CALL: roll_dice(sides=20)
   - Roll a die. sides must be: 4, 6, 8, 10, 12, 20, or 100
   - USE FOR: attack rolls, skill checks, saving throws
   - Example: Player attacks → TOOL_CALL: roll_dice(sides=20)
   - After getting the result, narrate and STOP. Do not roll again.

2. TOOL_CALL: check_inventory(character_id=1)
   - Returns what the character is carrying and their current HP
   - USE FOR: when player asks what they have
   - NEVER invent items — always use this tool
   - Example: "What am I carrying?" → TOOL_CALL: check_inventory(character_id=1)

3. TOOL_CALL: deal_damage(character_id=1, amount=10)
   - Reduces the PLAYER's HP permanently in the database
   - USE FOR: ONLY when an enemy attacks the PLAYER and deals damage
   - NEVER use this when the player is attacking an enemy
   - NEVER use this during the player's own attack action
   - Example: "Goblin hits me for 8" → TOOL_CALL: deal_damage(character_id=1, amount=8)

STRICT RULES:
- Call ONE tool per response, then wait for TOOL_RESULT
- After receiving TOOL_RESULT, give your narrative and STOP
- Never call the same tool twice in one exchange
- Never use deal_damage when the player is attacking
"""


def parse_tool_call(text: str):
    """
    Check if the LLM output contains a tool call.
    Handles multiple formats the model might use.
    """

    # Pattern 1: Ideal format with TOOL_CALL prefix
    pattern_with_prefix = r"TOOL_CALL:\s*(\w+)\(([^)]*)\)"
    match = re.search(pattern_with_prefix, text, re.IGNORECASE)

    if match:
        tool_name = match.group(1).lower()
        args_string = match.group(2)

    else:
        # Pattern 2: Model skipped the prefix
        tool_names = "|".join(AVAILABLE_TOOLS.keys())
        pattern_no_prefix = rf"({tool_names})\(([^)]*)\)"
        match = re.search(pattern_no_prefix, text, re.IGNORECASE)

        if not match:
            return None

        tool_name = match.group(1).lower()
        args_string = match.group(2)

    # Parse arguments string into a dictionary
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


def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    Look up and execute a tool by name.
    Returns a string description of the result.
    """

    if tool_name not in AVAILABLE_TOOLS:
        return f"Error: Tool '{tool_name}' does not exist."

    tool_function = AVAILABLE_TOOLS[tool_name]
    result = tool_function(**arguments)

    if result.get("success"):
        return result["description"]
    else:
        return f"Tool error: {result.get('error', 'Unknown error')}"


def run_agent(prompt: str, max_steps: int = 3) -> str:
    """
    The agent loop. Runs the LLM and handles tool calls.

    Reduced to max_steps=3 — one tool call should be enough
    for any single player action.
    """

    current_prompt = prompt
    steps = 0

    while steps < max_steps:
        steps += 1

        llm_response = ask_llm(current_prompt)
        tool_call = parse_tool_call(llm_response)

        if tool_call is None:
            # No tool call — clean and return final narrative
            cleaned = re.sub(r"TOOL_CALL:.*\n?", "", llm_response).strip()
            return cleaned

        # Tool call detected — execute it
        tool_name, arguments = tool_call
        print(f"[Agent] Calling tool: {tool_name}({arguments})")

        tool_result = execute_tool(tool_name, arguments)
        print(f"[Agent] Tool result: {tool_result}")

        # Feed result back — explicitly tell model to stop and narrate
        current_prompt = (
            current_prompt +
            f"\n{llm_response}"
            f"\nTOOL_RESULT: {tool_result}\n"
            f"\nNow give your final narrative response. "
            f"Do NOT call any more tools. Just describe what happened.\n"
            f"Dungeon Master:"
        )

    # Hit max_steps — clean leftover TOOL_CALL text before returning
    cleaned = re.sub(r"TOOL_CALL:.*\n?", "", llm_response).strip()
    return cleaned


# Test when run directly
if __name__ == "__main__":
    from app.rag.pipeline import retrieve_context, build_rag_prompt

    SYSTEM_PROMPT = """You are Aldric, a dramatic Dungeon Master.
You speak in an atmospheric, immersive tone.
Never break character.
Keep responses under 4 sentences."""

    full_system = SYSTEM_PROMPT + "\n\n" + TOOLS_DESCRIPTION

    test_scenarios = [
        {
            "scenario": "Player attacks",
            "messages": [
                {"role": "user", "content": "I attack the goblin with my sword!"}
            ]
        },
        {
            "scenario": "Player checks inventory",
            "messages": [
                {"role": "user", "content": "What am I carrying? My character id is 1"}
            ]
        },
        {
            "scenario": "Player takes damage",
            "messages": [
                {"role": "user",
                 "content": "The goblin hits me for 12 damage. My character id is 1"}
            ]
        }
    ]

    for test in test_scenarios:
        print(f"\n{'='*50}")
        print(f"Scenario: {test['scenario']}")
        print(f"Player: {test['messages'][-1]['content']}")
        print("-" * 50)

        context = retrieve_context(
            query=test["messages"][-1]["content"],
            messages=test["messages"]
        )

        prompt = build_rag_prompt(
            system_prompt=full_system,
            context=context,
            messages=test["messages"]
        )

        # Run the agent and display response
        response = run_agent(prompt)
        print(f"Aldric: {response}")