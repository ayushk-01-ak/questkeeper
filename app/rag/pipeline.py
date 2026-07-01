# app/rag/pipeline.py
# Connects retrieval and generation into one clean pipeline
# This is the heart of the RAG system

from sentence_transformers import SentenceTransformer
import chromadb
import os

# Reuse the same constants from embedder
CHROMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "chroma_store"
)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "questkeeper_lore"

# Load the embedding model ONCE at module level
# This means it loads when the app starts, not on every query
# Fixes the repeated "Loading weights" issue you saw
print("Loading embedding model into memory...")
_embedding_model = SentenceTransformer(EMBEDDING_MODEL)
print("Embedding model ready.")


def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Find relevant chunks for a query and return them as one string.

    Args:
        query: The player's message
        top_k: Number of chunks to retrieve

    Returns:
        A single string of relevant context from the PDF
    """
    # Connect to ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # Check if we have any documents stored
    if collection.count() == 0:
        # No documents indexed yet — return empty context
        return ""

    # Convert query to vector using the pre-loaded model
    query_embedding = _embedding_model.encode([query])

    # Find top_k most similar chunks
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=min(top_k, collection.count())
        # min() prevents asking for more results than we have
    )

    # Join the chunks into one readable block of context
    chunks = results["documents"][0]
    context = "\n\n---\n\n".join(chunks)

    return context


def build_rag_prompt(
    system_prompt: str,
    context: str,
    messages: list
) -> str:
    """
    Build a complete prompt that includes:
    - DM personality (system prompt)
    - Retrieved lore context
    - Full conversation history

    Args:
        system_prompt: Aldric's personality instructions
        context: Retrieved text chunks from the PDF
        messages: Full conversation history

    Returns:
        Complete prompt string ready to send to LLM
    """

    # Start with the system prompt (who Aldric is)
    full_prompt = f"SYSTEM: {system_prompt}\n\n"

    # Add retrieved context if we found any
    if context:
        full_prompt += "LORE CONTEXT (use this information to answer accurately):\n"
        full_prompt += context
        full_prompt += "\n\n"

    # Add full conversation history
    full_prompt += "CONVERSATION:\n"
    for message in messages:
        if message["role"] == "user":
            full_prompt += f"Player: {message['content']}\n"
        else:
            full_prompt += f"Dungeon Master: {message['content']}\n"

    # Cue for the model to respond as DM
    full_prompt += "Dungeon Master:"

    return full_prompt


# Test the complete pipeline when run directly
if __name__ == "__main__":
    from app.core.llm import ask_llm

    system_prompt = """You are Aldric, a wise and dramatic Dungeon Master.
You speak in an atmospheric, immersive tone.
When lore context is provided, use it accurately in your responses.
Keep responses under 4 sentences unless asked for more."""

    test_questions = [
        "Who is the Hollow King and where does he live?",
        "What are the rules for critical hits in this campaign?",
        "Tell me about Mira Thornquist"
    ]

    print("Testing RAG pipeline end to end...")
    print("=" * 50)

    for question in test_questions:
        print(f"\nPlayer: {question}")

        # Step 1: Retrieve relevant context
        context = retrieve_context(question)

        # Step 2: Build the complete prompt
        messages = [{"role": "user", "content": question}]
        prompt = build_rag_prompt(system_prompt, context, messages)

        # Step 3: Send to LLM and get response
        response = ask_llm(prompt)

        print(f"Aldric: {response}")
        print("-" * 50)