# app/core/llm.py
# This module handles all communication with our local Ollama LLM

import requests  # For making HTTP calls to Ollama's local server
import json      # For parsing the response data

# The URL where Ollama is always listening
OLLAMA_URL = "http://localhost:11434/api/generate"

# The model we downloaded
MODEL_NAME = "llama3.2:3b"


def ask_llm(prompt: str) -> str:
    """
    Send a prompt to the local LLM and return its response.
    
    Args:
        prompt: The text you want to send to the model
        
    Returns:
        The model's response as a string
    """
    
    # This is the data we send to Ollama
    # Think of it as filling out a form before submitting
    payload = {
        "model": MODEL_NAME,   # Which model to use
        "prompt": prompt,       # What to ask
        "stream": False         # Wait for full response before returning
    }
    
   # Send the request to Ollama's server
    response = requests.post(OLLAMA_URL, json=payload)
    
    # Convert the response from JSON to a Python dictionary
    data = response.json()
    
    # Extract just the text response from the data
    return data["response"]


# This block only runs if you run this file directly
# It won't run when other files import this module
if __name__ == "__main__":
    
    # Test prompt for our Dungeon Master
    test_prompt = "You are a Dungeon Master. Describe a tavern in 2 sentences."
    
    print("Sending prompt to LLM...")
    print(f"Prompt: {test_prompt}")
    print("-" * 40)
    
    result = ask_llm(test_prompt)
    
    print("Response from LLM:")
    print(result)