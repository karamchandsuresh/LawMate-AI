import os
import re


# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CLEANED_DATA_DIR = os.path.join(
    BASE_DIR,
    "cleaned_data"
)

CHUNKING_DIR = os.path.join(
    BASE_DIR,
    "chunking"
)

CHUNKS_FILE = os.path.join(
    CHUNKING_DIR,
    "legal_chunks.txt"
)


# ==========================================
# CHUNK SETTINGS
# ==========================================

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


# ==========================================
# TEXT CLEANUP
# ==========================================

def normalize_text(text):
    """
    Normalize whitespace while preserving
    paragraph and section boundaries.
    """

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Keep paragraph boundaries
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


# ==========================================
# CREATE CHUNKS
# ==========================================

def create_chunks(text):
    """
    Split legal text into overlapping chunks.
    """

    text = normalize_text(text)

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


# ==========================================
# PROCESS FILES
# ==========================================

def process_files():

    os.makedirs(
        CHUNKING_DIR,
        exist_ok=True
    )

    # Remove previous combined chunks file
    if os.path.exists(CHUNKS_FILE):
        os.remove(CHUNKS_FILE)

    files = [
        file
        for file in os.listdir(CLEANED_DATA_DIR)
        if file.endswith(".txt")
    ]

    print("Starting legal document chunking...")
    print(f"Found {len(files)} cleaned files.")
    print()

    total_chunks = 0

    with open(
        CHUNKS_FILE,
        "w",
        encoding="utf-8"
    ) as output_file:

        for filename in sorted(files):

            filepath = os.path.join(
                CLEANED_DATA_DIR,
                filename
            )

            print(f"Processing: {filename}")

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as file:

                text = file.read()

            chunks = create_chunks(text)

            print(
                f"Chunks created: {len(chunks)}"
            )

            for index, chunk in enumerate(
                chunks,
                start=1
            ):

                output_file.write(
                    f"\n{'=' * 80}\n"
                )

                output_file.write(
                    f"SOURCE: {filename}\n"
                )

                output_file.write(
                    f"CHUNK: {index}\n"
                )

                output_file.write(
                    f"{'=' * 80}\n"
                )

                output_file.write(
                    chunk
                )

                output_file.write("\n")

            total_chunks += len(chunks)

            print()

    print("==========================================")
    print("Chunking completed successfully.")
    print(f"Total chunks created: {total_chunks}")
    print(f"Saved to: {CHUNKS_FILE}")
    print("==========================================")


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    process_files()