import os
import chromadb


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHUNKS_FILE = os.path.join(
    BASE_DIR,
    "chunking",
    "legal_chunks.txt"
)

EMBEDDINGS_FILE = os.path.join(
    BASE_DIR,
    "embeddings",
    "legal_embeddings.txt"
)

CHROMA_DIR = os.path.join(
    BASE_DIR,
    "chroma_db"
)


# --------------------------------------------------
# Start ChromaDB
# --------------------------------------------------

print("Starting ChromaDB storage...")

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_or_create_collection(
    name="legal_documents"
)

print("ChromaDB collection ready.")


# --------------------------------------------------
# Read legal chunks
# --------------------------------------------------

print("Reading legal chunks...")

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    content = file.read()


# --------------------------------------------------
# Parse chunks
# --------------------------------------------------

chunks = []

# Every chunk begins with:
#
# SOURCE: filename
# CHUNK: number
# ========
#
# Therefore split using CHUNK:

parts = content.split("CHUNK:")

for part in parts[1:]:

    lines = part.splitlines()

    # First line is chunk number
    chunk_number = lines[0].strip()

    # Find separator after CHUNK number
    separator_index = None

    for i, line in enumerate(lines):

        if line.strip().startswith("="):

            separator_index = i
            break

    if separator_index is None:
        continue

    # Everything after separator is legal text
    legal_text = "\n".join(
        lines[separator_index + 1:]
    ).strip()

    if legal_text:

        chunks.append(legal_text)


print(f"Chunks found: {len(chunks)}")


# --------------------------------------------------
# Read embeddings
# --------------------------------------------------

print("Reading embeddings...")

embeddings = []
embedding_ids = []

with open(
    EMBEDDINGS_FILE,
    "r",
    encoding="utf-8"
) as file:

    lines = file.readlines()


current_id = None
current_embedding = []


for line in lines:

    line = line.strip()

    if not line:
        continue

    # Example:
    # CHUNK_1
    if line.startswith("CHUNK_"):

        # Save previous embedding
        if current_id is not None:

            embeddings.append(current_embedding)
            embedding_ids.append(current_id)

        current_id = line
        current_embedding = []

    else:

        values = line.split(",")

        current_embedding.extend(
            float(value)
            for value in values
        )


# Save final embedding
if current_id is not None:

    embeddings.append(current_embedding)
    embedding_ids.append(current_id)


print(f"Embeddings found: {len(embeddings)}")


# --------------------------------------------------
# Validate
# --------------------------------------------------

if len(chunks) != len(embeddings):

    raise ValueError(
        f"Mismatch between chunks and embeddings: "
        f"{len(chunks)} chunks vs "
        f"{len(embeddings)} embeddings"
    )


# --------------------------------------------------
# Store in ChromaDB
# --------------------------------------------------

print("Storing embeddings in ChromaDB...")

collection.upsert(
    ids=embedding_ids,
    embeddings=embeddings,
    documents=chunks,
    metadatas=[
        {
            "chunk_id": embedding_ids[i]
        }
        for i in range(len(chunks))
    ]
)


# --------------------------------------------------
# Verify
# --------------------------------------------------

count = collection.count()

print()
print("ChromaDB storage completed successfully.")
print(f"Documents stored: {count}")
print(f"Collection name: {collection.name}")
print(f"Database location: {CHROMA_DIR}")