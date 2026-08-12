import os
import re


# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DATA_DIR = os.path.join(BASE_DIR, "raw_data")
CLEANED_DATA_DIR = os.path.join(BASE_DIR, "cleaned_data")


# Create cleaned_data folder if it does not exist
os.makedirs(CLEANED_DATA_DIR, exist_ok=True)


# ==========================================
# CLEAN TEXT FUNCTION
# ==========================================

def clean_text(text):
    """
    Cleans scraped legal text while preserving
    important legal information and section structure.
    """

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove common website navigation text
    unwanted_lines = {
        "Screen Reader Access",
        "A-",
        "A",
        "A+",
        "T",
        "Language",
        "हिंदी",
        "English",
        "Skip navigation",
        "Show Related Subordinates",
    }

    lines = text.split("\n")

    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            cleaned_lines.append("")
            continue

        if line in unwanted_lines:
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Remove excessive blank lines again
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


# ==========================================
# PROCESS ONE FILE
# ==========================================

def process_file(filename):
    raw_path = os.path.join(RAW_DATA_DIR, filename)

    cleaned_path = os.path.join(
        CLEANED_DATA_DIR,
        filename
    )

    print(f"Processing: {filename}")

    try:
        with open(raw_path, "r", encoding="utf-8") as file:
            text = file.read()

        cleaned_text = clean_text(text)

        with open(
            cleaned_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(cleaned_text)

        print(
            f"Saved cleaned file: {cleaned_path}"
        )

        print(
            f"Characters: {len(text)} → {len(cleaned_text)}"
        )

    except Exception as e:
        print(f"Error processing {filename}: {e}")


# ==========================================
# PROCESS ALL RAW FILES
# ==========================================

def main():

    print("Starting legal data cleaning...")
    print()

    files = [
        file
        for file in os.listdir(RAW_DATA_DIR)
        if file.endswith(".txt")
    ]

    if not files:
        print("No .txt files found in raw_data.")
        return

    print(f"Found {len(files)} raw files.")
    print()

    for filename in files:
        process_file(filename)

    print()
    print("==========================================")
    print("Data cleaning completed successfully.")
    print("==========================================")


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    main()