# app/memory/summarizer.py
# Uses the LLM to summarize completed sessions
# Compresses long conversations into short memorable summaries

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.llm import ask_llm
from app.db.memory import get_session_messages, save_session_summary


def summarize_session(session_id: int) -> str:
    """
    Ask the LLM to summarize everything that happened in a session.
    Saves the summary to the database and returns it.

    Args:
        session_id: The session to summarize

    Returns:
        The summary string
    """

    # Get all messages from this session
    messages = get_session_messages(session_id)

    if not messages:
        return "No events to summarize."

    # Build a readable transcript for the LLM to summarize
    transcript = ""
    for msg in messages:
        prefix = "Player" if msg["role"] == "user" else "Dungeon Master"
        transcript += f"{prefix}: {msg['content']}\n"

    # Ask the LLM for a compact summary
    # This is a one-off call, not part of the agent loop
    summary_prompt = f"""You are summarizing a D&D campaign session.
Read the following conversation and write a brief summary (3-5 sentences).
Include: where the player went, who they met, what happened,
any items gained or lost, and current HP if mentioned.
Write in past tense. Be specific about names and places.

SESSION TRANSCRIPT:
{transcript}

SUMMARY:"""

    summary = ask_llm(summary_prompt)

    # Save summary to database
    save_session_summary(session_id, summary)

    return summary


# Test when run directly
if __name__ == "__main__":
    from app.db.database import initialize_database
    from app.db.memory import create_session, save_message

    initialize_database()

    # Create a test session with fake messages
    print("Creating test session...")
    session_id = create_session(character_id=1)

    # Simulate a short adventure
    test_messages = [
        ("user", "I enter the Ashlands carefully"),
        ("assistant", "The ash swirls around your boots as you step into the blighted shard. The air tastes of sulfur and old magic."),
        ("user", "I search for the Soulshard"),
        ("assistant", "After an hour of searching through ruins, you discover a glowing crystal fragment near Karneth Hollow. It pulses with dark energy."),
        ("user", "I pick it up and head back"),
        ("assistant", "As you reach for the Soulshard, an ash wraith materializes. You take 20 damage before managing to flee with the crystal.")
    ]

    for role, content in test_messages:
        save_message(session_id, character_id=1, role=role, content=content)

    print(f"Saved {len(test_messages)} messages")
    print("\nGenerating summary...")

    summary = summarize_session(session_id)

    print("\nSession Summary:")
    print("-" * 40)
    print(summary)