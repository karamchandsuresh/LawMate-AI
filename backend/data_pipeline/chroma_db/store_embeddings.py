import os
import re
import chromadb


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

EMBEDDINGS_FILE = os.path.join(
    BASE_DIR,
    "embeddings",
    "legal_embeddings.txt"
)

CHROMA_DIR = os.path.join(
    BASE_DIR,
    "chroma_db"
)

COLLECTION_NAME = "legal_documents"


# ============================================================
# START
# ============================================================

print("=" * 70)
print("LAWMATE AI - CHROMADB STORAGE")
print("=" * 70)


# ============================================================
# READ AND PARSE LEGAL CHUNKS
# ============================================================

print("\nReading legal chunks...")

with open(
    CHUNKS_FILE,
    "r",
    encoding="utf-8"
) as file:

    chunks_content = file.read()


chunk_pattern = (
    r"(?ms)"
    r"^SOURCE_TYPE:\s*(.*?)\n"
    r"SOURCE_FILE:\s*(.*?)\n"
    r"CHUNK:\s*(\d+)\n"
    r"={3,}\n"
    r"(.*?)"
    r"(?=^={3,}\nSOURCE_TYPE:|\Z)"
)

chunk_matches = re.findall(
    chunk_pattern,
    chunks_content
)


documents = []
chunk_metadata = []


for (
    source_type,
    source_file,
    chunk_number,
    chunk_text
) in chunk_matches:

    chunk_text = chunk_text.strip()

    if not chunk_text:
        continue

    documents.append(
        chunk_text
    )

    chunk_metadata.append(
        {
            "source_type": source_type.strip(),
            "source_file": source_file.strip(),
            "source_chunk": int(chunk_number)
        }
    )


print(
    f"Legal chunks found: "
    f"{len(documents)}"
)


if not documents:

    raise ValueError(
        "No legal chunks were found. "
        "Check legal_chunks.txt."
    )


# ============================================================
# READ AND PARSE EMBEDDINGS
# ============================================================

print("\nReading embeddings...")

with open(
    EMBEDDINGS_FILE,
    "r",
    encoding="utf-8"
) as file:

    embeddings_content = file.read()


embedding_pattern = (
    r"(?ms)"
    r"CHUNK_ID:\s*(\d+)\n"
    r"SOURCE_TYPE:\s*(.*?)\n"
    r"SOURCE_FILE:\s*(.*?)\n"
    r"SOURCE_CHUNK:\s*(\d+)\n"
    r"EMBEDDING:\n"
    r"(.*?)(?=\n\nCHUNK_ID:|\Z)"
)

embedding_matches = re.findall(
    embedding_pattern,
    embeddings_content
)


embeddings = []
embedding_metadata = []
ids = []


for (
    chunk_id,
    source_type,
    source_file,
    source_chunk,
    embedding_text
) in embedding_matches:

    values = [
        float(value)
        for value in embedding_text.strip().split(",")
        if value.strip()
    ]

    if not values:
        continue

    embeddings.append(
        values
    )

    embedding_metadata.append(
        {
            "source_type": source_type.strip(),
            "source_file": source_file.strip(),
            "source_chunk": int(source_chunk)
        }
    )

    ids.append(
        f"legal_chunk_{int(chunk_id):05d}"
    )


print(
    f"Embeddings found: "
    f"{len(embeddings)}"
)


# ============================================================
# VALIDATE COUNTS
# ============================================================

if len(documents) != len(embeddings):

    raise ValueError(
        "Chunk/embedding mismatch: "
        f"{len(documents)} chunks vs "
        f"{len(embeddings)} embeddings."
    )


if len(documents) != len(chunk_metadata):

    raise ValueError(
        "Chunk metadata count does not match "
        "document count."
    )


if len(embeddings) != len(
    embedding_metadata
):

    raise ValueError(
        "Embedding metadata count does not match "
        "embedding count."
    )


# ============================================================
# VALIDATE METADATA ALIGNMENT
# ============================================================

print(
    "\nValidating chunk metadata..."
)


for index in range(
    len(documents)
):

    chunk_meta = chunk_metadata[index]

    embedding_meta = embedding_metadata[index]

    if (
        chunk_meta["source_type"]
        != embedding_meta["source_type"]
    ):

        raise ValueError(
            f"Source type mismatch at "
            f"chunk {index + 1}"
        )

    if (
        chunk_meta["source_file"]
        != embedding_meta["source_file"]
    ):

        raise ValueError(
            f"Source file mismatch at "
            f"chunk {index + 1}"
        )

    if (
        chunk_meta["source_chunk"]
        != embedding_meta["source_chunk"]
    ):

        raise ValueError(
            f"Source chunk mismatch at "
            f"chunk {index + 1}"
        )


print(
    "Chunk metadata validation successful."
)


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

print("\nConnecting to ChromaDB...")

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

print(
    f"Database location: "
    f"{CHROMA_DIR}"
)


# ============================================================
# REBUILD COLLECTION
# ============================================================

existing_collections = [
    collection.name
    for collection
    in client.list_collections()
]


if COLLECTION_NAME in existing_collections:

    print(
        "Removing old legal_documents "
        "collection..."
    )

    client.delete_collection(
        name=COLLECTION_NAME
    )


collection = client.create_collection(
    name=COLLECTION_NAME
)

print(
    "Fresh ChromaDB collection created."
)


# ============================================================
# PREPARE FINAL METADATA
# ============================================================

metadatas = []


for index, meta in enumerate(
    chunk_metadata
):

    metadatas.append(
        {
            "chunk_id": ids[index],
            "source_type": meta[
                "source_type"
            ],
            "source_file": meta[
                "source_file"
            ],
            "source_chunk": meta[
                "source_chunk"
            ]
        }
    )


# ============================================================
# STORE DATA
# ============================================================

print(
    "\nStoring legal documents and "
    "embeddings in ChromaDB..."
)

collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)


# ============================================================
# VERIFY STORAGE
# ============================================================

stored_count = collection.count()


print()
print("=" * 70)
print("CHROMADB STORAGE COMPLETE")
print("=" * 70)

print(
    f"Documents stored: "
    f"{stored_count}"
)

print(
    f"Collection name: "
    f"{COLLECTION_NAME}"
)

print(
    f"Database location: "
    f"{CHROMA_DIR}"
)


# ============================================================
# FINAL SAFETY CHECK
# ============================================================

if stored_count != len(documents):

    raise ValueError(
        "ChromaDB document count does not "
        "match the expected number."
    )


print(
    "\nChromaDB verification successful."
)