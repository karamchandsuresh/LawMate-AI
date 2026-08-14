import os
import re


# ============================================================
# PATH CONFIGURATION
# ============================================================

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


# ============================================================
# LEGAL DATA SOURCES
# ============================================================

SOURCE_FOLDERS = [
    "india_code",
    "supreme_court",
    "gazette",
    "law_commission",
    "high_court",
]


# ============================================================
# CHUNK SETTINGS
# ============================================================

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):
    """
    Normalize whitespace while preserving
    useful legal structure.
    """

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces and tabs
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# CREATE CHUNKS
# ============================================================

def create_chunks(text):
    """
    Split legal text into overlapping chunks.
    """

    text = normalize_text(text)

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[
            start:end
        ].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


# ============================================================
# PROCESS ONE SOURCE
# ============================================================

def process_source(
    source_name,
    output_file
):
    """
    Process all cleaned documents for one source.
    """

    source_dir = os.path.join(
        CLEANED_DATA_DIR,
        source_name
    )

    if not os.path.exists(source_dir):

        print(
            f"Source folder not found: "
            f"{source_name}"
        )

        return 0

    files = [
        filename
        for filename in os.listdir(
            source_dir
        )
        if filename.lower().endswith(
            ".txt"
        )
    ]

    if not files:

        print(
            f"No cleaned documents found for: "
            f"{source_name}"
        )

        return 0

    print()
    print("=" * 70)

    print(
        f"SOURCE: {source_name.upper()}"
    )

    print("=" * 70)

    print(
        f"Documents found: {len(files)}"
    )

    source_chunk_count = 0

    for filename in sorted(files):

        filepath = os.path.join(
            source_dir,
            filename
        )

        print()
        print(
            f"Processing: "
            f"{source_name}/{filename}"
        )

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()

        chunks = create_chunks(
            text
        )

        print(
            f"Chunks created: {len(chunks)}"
        )

        for chunk_index, chunk in enumerate(
            chunks,
            start=1
        ):

            output_file.write(
                f"\n{'=' * 80}\n"
            )

            output_file.write(
                f"SOURCE_TYPE: {source_name}\n"
            )

            output_file.write(
                f"SOURCE_FILE: {filename}\n"
            )

            output_file.write(
                f"CHUNK: {chunk_index}\n"
            )

            output_file.write(
                f"{'=' * 80}\n"
            )

            output_file.write(
                chunk
            )

            output_file.write("\n")

        source_chunk_count += len(
            chunks
        )

    print()
    print(
        f"Total chunks for {source_name}: "
        f"{source_chunk_count}"
    )

    return source_chunk_count


# ============================================================
# MAIN PROCESS
# ============================================================

def process_files():

    os.makedirs(
        CHUNKING_DIR,
        exist_ok=True
    )

    # Remove the old generated chunks file
    if os.path.exists(CHUNKS_FILE):
        os.remove(CHUNKS_FILE)

    print("=" * 70)
    print("LAWMATE AI - LEGAL DOCUMENT CHUNKING")
    print("=" * 70)

    total_chunks = 0

    with open(
        CHUNKS_FILE,
        "w",
        encoding="utf-8"
    ) as output_file:

        for source_name in SOURCE_FOLDERS:

            source_chunks = process_source(
                source_name,
                output_file
            )

            total_chunks += source_chunks

    print()
    print("=" * 70)
    print("CHUNKING COMPLETE")
    print("=" * 70)

    print(
        f"Total chunks created: "
        f"{total_chunks}"
    )

    print(
        f"Saved to: "
        f"{CHUNKS_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    process_files()
