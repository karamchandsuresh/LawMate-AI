import os
import re
from sentence_transformers import SentenceTransformer


# ==============================
# PATH CONFIGURATION
# ==============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHUNKS_FILE = os.path.join(
    BASE_DIR,
    "chunking",
    "legal_chunks.txt"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "embeddings",
    "legal_embeddings.txt"
)


# ==============================
# LOAD EMBEDDING MODEL
# ==============================

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded successfully.")


# ==============================
# READ LEGAL CHUNKS
# ==============================

print("\nReading legal chunks...")

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    content = file.read()


# ==============================
# EXTRACT ACTUAL CHUNK BLOCKS
# ==============================

pattern = r"(?ms)^SOURCE:.*?\nCHUNK:\s*\d+\n={3,}\n(.*?)(?=^SOURCE:|\Z)"

matches = re.findall(pattern, content)

chunks = [
    chunk.strip()
    for chunk in matches
    if chunk.strip()
]

print(f"Chunks found: {len(chunks)}")


# ==============================
# VALIDATE CHUNKS
# ==============================

if not chunks:
    raise ValueError(
        "No legal chunks were found in legal_chunks.txt."
    )


# ==============================
# GENERATE EMBEDDINGS
# ==============================

print("\nGenerating embeddings...")

embeddings = model.encode(
    chunks,
    show_progress_bar=True
)

print("Embeddings generated successfully.")


# ==============================
# SAVE EMBEDDINGS
# ==============================

print("\nSaving embeddings...")

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    for index, embedding in enumerate(embeddings):

        file.write(f"CHUNK_{index + 1}\n")

        file.write(
            ",".join(str(value) for value in embedding)
        )

        file.write("\n\n")


# ==============================
# COMPLETION
# ==============================

print("\nEmbedding process completed.")
print(f"Saved to: {OUTPUT_FILE}")
print(f"Embeddings created: {len(embeddings)}")