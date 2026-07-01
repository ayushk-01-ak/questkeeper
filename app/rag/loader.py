# app/rag/loader.py
# Extracts text from PDFs and splits it into manageable chunks

import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Read a PDF file and return all its text as one big string.
    """
    full_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        # Loop through every page in the PDF
        for page in pdf.pages:
            page_text = page.extract_text()

            # Some pages might be blank or unreadable
            if page_text:
                full_text += page_text + "\n"

    return full_text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
    """
    Split a long text into overlapping chunks.

    Args:
        text: The full text to split
        chunk_size: Target number of characters per chunk
        overlap: How many characters chunks should share with neighbors

    Returns:
        A list of text chunks
    """

    chunks = []
    start = 0

    while start < len(text):
        # Take a slice of text from start to start+chunk_size
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk.strip())

        # Move start forward, but step back by 'overlap'
        # This way each chunk shares some text with the previous one
        # Overlap prevents losing context at chunk boundaries
        start = end - overlap

    return chunks


# Test this module directly
if __name__ == "__main__":
    text = extract_text_from_pdf("data/questkeeper_lore.pdf")

    print(f"Extracted {len(text)} characters total")
    print("-" * 40)
    print("First 300 characters:")
    print(text[:300])

    print("-" * 40)

    chunks = chunk_text(text)
    print(f"Split into {len(chunks)} chunks")
    print("-" * 40)
    print("First chunk:")
    print(chunks[0])
    print("-" * 40)
    print("Second chunk:")
    print(chunks[1])