# app/core/llm.py
import requests
import json
import os

# When running in Docker, Ollama is on the host machine
# OLLAMA_HOST environment variable lets us configure this
# Default falls back to localhost for running outside Docker
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate"
MODEL_NAME = "llama3.2:3b"


def ask_llm(prompt: str) -> str:
    """
    Send a single prompt to the LLM and return response.
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
    Send conversation history to the LLM and return response.
    """
    full_prompt = f"SYSTEM: {system_prompt}\n\n"

    for message in messages:
        if message["role"] == "user":
            full_prompt += f"Player: {message['content']}\n"
        else:
            full_prompt += f"Dungeon Master: {message['content']}\n"

    full_prompt += "Dungeon Master:"

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    data = response.json()
    return data["response"]


if __name__ == "__main__":
    test_prompt = "You are a Dungeon Master. Describe a tavern in 2 sentences."
    print("Sending prompt to LLM...")
    result = ask_llm(test_prompt)
    print("Response:")
    print(result)