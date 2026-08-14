import os
import re
from sentence_transformers import SentenceTransformer


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

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


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("=" * 70)
print("LAWMATE AI - EMBEDDING GENERATION")
print("=" * 70)

print("\nLoading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully.")


# ============================================================
# READ CHUNKS FILE
# ============================================================

print("\nReading legal chunks...")

with open(
    CHUNKS_FILE,
    "r",
    encoding="utf-8"
) as file:

    content = file.read()


# ============================================================
# PARSE CHUNKS
# ============================================================

pattern = (
    r"(?ms)"
    r"^SOURCE_TYPE:\s*(.*?)\n"
    r"SOURCE_FILE:\s*(.*?)\n"
    r"CHUNK:\s*(\d+)\n"
    r"={3,}\n"
    r"(.*?)"
    r"(?=^={3,}\nSOURCE_TYPE:|\Z)"
)

matches = re.findall(
    pattern,
    content
)


chunks = []
metadata = []

for source_type, source_file, chunk_number, chunk_text in matches:

    chunk_text = chunk_text.strip()

    if not chunk_text:
        continue

    chunks.append(
        chunk_text
    )

    metadata.append(
        {
            "source_type": source_type.strip(),
            "source_file": source_file.strip(),
            "chunk_number": int(chunk_number)
        }
    )


print(
    f"Chunks found: {len(chunks)}"
)


# ============================================================
# VALIDATION
# ============================================================

if not chunks:

    raise ValueError(
        "No legal chunks found. "
        "Check legal_chunks.txt format."
    )


# ============================================================
# GENERATE EMBEDDINGS
# ============================================================

print("\nGenerating embeddings...")

embeddings = model.encode(
    chunks,
    show_progress_bar=True
)

print(
    "Embeddings generated successfully."
)


# ============================================================
# SAVE EMBEDDINGS
# ============================================================

print("\nSaving embeddings...")

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    for index, embedding in enumerate(
        embeddings
    ):

        meta = metadata[index]

        file.write(
            f"CHUNK_ID: {index + 1}\n"
        )

        file.write(
            f"SOURCE_TYPE: "
            f"{meta['source_type']}\n"
        )

        file.write(
            f"SOURCE_FILE: "
            f"{meta['source_file']}\n"
        )

        file.write(
            f"SOURCE_CHUNK: "
            f"{meta['chunk_number']}\n"
        )

        file.write(
            "EMBEDDING:\n"
        )

        file.write(
            ",".join(
                str(value)
                for value in embedding
            )
        )

        file.write(
            "\n\n"
        )


# ============================================================
# COMPLETION
# ============================================================

print()
print("=" * 70)
print("EMBEDDING GENERATION COMPLETE")
print("=" * 70)

print(
    f"Embeddings created: "
    f"{len(embeddings)}"
)

print(
    f"Saved to: "
    f"{OUTPUT_FILE}"
)