# app/core/llm.py
# Handles all communication with our local Ollama LLM

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def ask_llm(prompt: str) -> str:
    """
    Send a single prompt to the LLM and return response.
    Used for simple one-off questions with no history.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    data = response.json()
    return data["response"]


def ask_llm_with_history(messages: list, system_prompt: str) -> str:
    """
    Send a conversation history to the LLM and return response.
    
    This is the real way to maintain context across messages.
    
    Args:
        messages: List of dicts like [{"role": "user", "content": "..."},
                                      {"role": "assistant", "content": "..."}]
        system_prompt: The personality/instructions for the DM
        
    Returns:
        The model's response as a string
    """

    # We build one big prompt string that includes everything
    # This is called "prompt engineering" - structuring input carefully
    full_prompt = f"SYSTEM: {system_prompt}\n\n"

    # Loop through every previous message and add it to the prompt
    for message in messages:
        if message["role"] == "user":
            # Prefix user messages with "Player:"
            full_prompt += f"Player: {message['content']}\n"
        else:
            # Prefix assistant messages with "Dungeon Master:"
            full_prompt += f"Dungeon Master: {message['content']}\n"

    # Finally add the cue for the model to respond
    # The model will complete whatever comes after "Dungeon Master:"
    full_prompt += "Dungeon Master:"

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    data = response.json()
    return data["response"]