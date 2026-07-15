# app/rag/embedder.py
# Converts text chunks into vectors and stores them in ChromaDB

import chromadb
from sentence_transformers import SentenceTransformer
import os

# Where ChromaDB will store its data on disk
# This persists between runs — like SQLite but for vectors
CHROMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_store"
)

# The embedding model name
# all-MiniLM-L6-v2 is small (~80MB), fast, and good enough for our use case
# It was designed specifically for semantic similarity tasks
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Collection name — like a table name in ChromaDB
COLLECTION_NAME = "questkeeper_lore"


def get_chroma_collection():
    """
    Create or connect to our ChromaDB collection.
    Safe to call multiple times — returns existing collection if it exists.
    """
    # PersistentClient saves data to disk so it survives restarts
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # get_or_create means: use existing collection OR create new one
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        # cosine = measure similarity by angle between vectors
        # better for text than raw distance
    )

    return collection


def embed_and_store(chunks: list) -> None:
    """
    Convert text chunks to vectors and store in ChromaDB.

    Args:
        chunks: List of text strings from the PDF loader
    """
    print("Loading embedding model...")
    # Load the small embedding model
    # First run downloads it, subsequent runs load from cache
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f"Embedding {len(chunks)} chunks...")
    # Convert all chunks to vectors at once
    # Each chunk becomes a list of ~384 numbers
    embeddings = model.encode(chunks)

    # Get or create our ChromaDB collection
    collection = get_chroma_collection()

    # Check how many documents are already stored
    existing = collection.count()
    if existing > 0:
        print(f"Collection already has {existing} chunks. Clearing before reload...")
        # Delete all existing entries so we don't duplicate
        collection.delete(where={"source": {"$exists": True}})

    # Store everything in ChromaDB
    # Each chunk needs: an id, the embedding vector, and the original text
    collection.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        embeddings=embeddings.tolist(),
        documents=chunks,
        metadatas=[
            {"source": "questkeeper_lore.pdf", "chunk_index": i}
            for i in range(len(chunks))
        ],
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB at: {CHROMA_PATH}")


def retrieve_relevant_chunks(query: str, top_k: int = 3) -> list:
    """
    Find the most relevant chunks for a given query.

    Args:
        query: The player's question or message
        top_k: How many chunks to retrieve

    Returns:
        List of relevant text strings
    """
    # Load the same embedding model we used to store
    # MUST be the same model — vectors only compare if created the same way
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Convert the query to a vector
    query_embedding = model.encode([query])

    # Get our collection
    collection = get_chroma_collection()

    # Ask ChromaDB for the top_k most similar chunks
    results = collection.query(
        query_embeddings=query_embedding.tolist(), n_results=top_k
    )

    # results["documents"] is a list of lists, we want the inner list
    return results["documents"][0]


# Test when run directly
if __name__ == "__main__":
    from app.rag.loader import extract_text_from_pdf, chunk_text

    # Step 1: Load and chunk the PDF
    print("Loading PDF...")
    text = extract_text_from_pdf("data/questkeeper_lore.pdf")
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks")

    # Step 2: Embed and store
    embed_and_store(chunks)

    # Step 3: Test retrieval
    print("\nTesting retrieval...")
    print("-" * 40)

    test_queries = [
        "Who is the Hollow King?",
        "What happens on a critical hit?",
        "Tell me about Mira Thornquist",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        relevant = retrieve_relevant_chunks(query, top_k=2)
        print(f"Top result:\n{relevant[0][:300]}...")
        print("-" * 40)
