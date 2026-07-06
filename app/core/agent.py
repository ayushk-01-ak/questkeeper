# app/core/agent.py
# The agent loop - bridges the LLM and our tools
# Detects tool calls in LLM output and executes them

import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.llm import ask_llm
from app.core.tools import AVAILABLE_TOOLS


# Tell the LLM exactly what tools exist and how to call them
# This gets added to every prompt so Aldric always knows his abilities
TOOLS_DESCRIPTION = """
You have access to the following tools. Use them when the situation calls for it.
To use a tool, output EXACTLY this format on its own line:
TOOL_CALL: tool_name(arg1=value1, arg2=value2)

Available tools:

TOOL_CALL: roll_dice(sides=20)
→ Roll a die. sides must be one of: 4, 6, 8, 10, 12, 20, 100
→ Use for: attacks, skill checks, saving throws, any random outcome

TOOL_CALL: check_inventory(character_id=1)
→ Check what a character is carrying and their current HP
→ Use for: inventory questions, item checks

TOOL_CALL: deal_damage(character_id=1, amount=10)
→ Apply damage to a character and update their HP permanently
→ Use for: whenever a character takes damage in combat

Rules:
- Only use a tool when it genuinely adds to the game
- After a tool result, continue the narrative naturally
- Never make up dice results — always use roll_dice
- Always deal damage using deal_damage, never just narrate it
"""


def parse_tool_call(text: str):
    """
    Check if the LLM output contains a tool call.
    If yes, extract the tool name and arguments.
    If no, return None.

    Example input:  "TOOL_CALL: roll_dice(sides=20)"
    Example output: ("roll_dice", {"sides": 20})
    """

    # Look for the TOOL_CALL pattern anywhere in the text
    pattern = r"TOOL_CALL:\s*(\w+)\(([^)]*)\)"
    match = re.search(pattern, text)

    if not match:
        # No tool call found — normal response
        return None

    tool_name = match.group(1)        # e.g. "roll_dice"
    args_string = match.group(2)      # e.g. "sides=20"

    # Parse the arguments string into a dictionary
    # "sides=20, character_id=1" → {"sides": 20, "character_id": 1}
    arguments = {}

    if args_string.strip():
        # Split by comma to get individual arguments
        for arg in args_string.split(","):
            arg = arg.strip()
            if "=" in arg:
                key, value = arg.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Convert to correct Python type
                # Try integer first, then float, then keep as string
                try:
                    arguments[key] = int(value)
                except ValueError:
                    try:
                        arguments[key] = float(value)
                    except ValueError:
                        # Remove quotes if present
                        arguments[key] = value.strip("\"'")

    return tool_name, arguments


def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    Look up and execute a tool by name.
    Returns a string description of the result.

    Args:
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments to pass

    Returns:
        String result to feed back to the LLM
    """

    # Check if tool exists
    if tool_name not in AVAILABLE_TOOLS:
        return f"Error: Tool '{tool_name}' does not exist."

    # Get the function from our dictionary
    tool_function = AVAILABLE_TOOLS[tool_name]

    # Call the function with the parsed arguments
    result = tool_function(**arguments)

    # Return the human readable description
    if result.get("success"):
        return result["description"]
    else:
        return f"Tool error: {result.get('error', 'Unknown error')}"


def run_agent(prompt: str, max_steps: int = 5) -> str:
    """
    The agent loop. Runs the LLM and handles tool calls.

    This loop continues until:
    - The LLM gives a normal response (no tool call)
    - We hit max_steps (prevents infinite loops)

    Args:
        prompt: The full prompt to send to the LLM
        max_steps: Maximum number of tool calls allowed per response

    Returns:
        Final narrative response to show the player
    """

    current_prompt = prompt
    steps = 0

    while steps < max_steps:
        steps += 1

        # Ask the LLM for a response
        llm_response = ask_llm(current_prompt)

        # Check if the response contains a tool call
        tool_call = parse_tool_call(llm_response)

        if tool_call is None:
            # No tool call — this is the final narrative response
            return llm_response

        # Tool call detected — execute it
        tool_name, arguments = tool_call
        print(f"[Agent] Calling tool: {tool_name}({arguments})")

        tool_result = execute_tool(tool_name, arguments)
        print(f"[Agent] Tool result: {tool_result}")

        # Feed the tool result back into the prompt
        # The LLM sees what happened and continues the narrative
        current_prompt = (
            current_prompt +
            f"\n{llm_response}" +           # What LLM said including tool call
            f"\nTOOL_RESULT: {tool_result}" # What the tool returned
            f"\nDungeon Master:"            # Cue to continue
        )

    # If we hit max_steps, return whatever the last response was
    return llm_response


# Test the agent when run directly
if __name__ == "__main__":
    from app.rag.pipeline import retrieve_context, build_rag_prompt

    SYSTEM_PROMPT = """You are Aldric, a dramatic Dungeon Master.
You speak in an atmospheric, immersive tone.
Never break character.
Keep responses under 4 sentences."""

    # Combine system prompt with tools description
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

        # Build prompt with tools knowledge
        context = retrieve_context(
            query=test["messages"][-1]["content"],
            messages=test["messages"]
        )

        prompt = build_rag_prompt(
            system_prompt=full_system,
            context=context,
            messages=test["messages"]
        )

        response = run_agent(prompt)
        print(f"Aldric: {response}")