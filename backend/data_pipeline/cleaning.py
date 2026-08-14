import os
import re


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

RAW_DATA_DIR = os.path.join(
    BASE_DIR,
    "raw_data"
)

CLEANED_DATA_DIR = os.path.join(
    BASE_DIR,
    "cleaned_data"
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
# COMMON WEBSITE TEXT TO REMOVE
# ============================================================

UNWANTED_LINES = {
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
    "Show all section",
    "Rules",
    "Regulations",
    "Notifications",
    "Orders",
    "Circulars",
    "Ordinance",
    "Statutes",
    "Sections",
    "Schedule",
    "Annexure",
    "Appendix",
    "Forms",
    "Actdetails",
    "Close",
    "×",
}


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):
    """
    Clean scraped legal text while preserving important
    legal content, metadata, headings and section text.
    """

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove tabs and excessive spaces
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    cleaned_lines = []

    previous_line = None

    for line in text.splitlines():

        line = line.strip()

        # Skip empty lines for now
        if not line:
            continue

        # Remove known website navigation text
        if line in UNWANTED_LINES:
            continue

        # Remove consecutive duplicates
        if line == previous_line:
            continue

        cleaned_lines.append(line)

        previous_line = line

    cleaned_text = "\n".join(
        cleaned_lines
    )

    return cleaned_text.strip()


# ============================================================
# PROCESS ONE FILE
# ============================================================

def process_file(
    source_name,
    filename
):
    """
    Clean one raw legal document and store it inside
    the corresponding cleaned_data source folder.
    """

    raw_file = os.path.join(
        RAW_DATA_DIR,
        source_name,
        filename
    )

    cleaned_source_dir = os.path.join(
        CLEANED_DATA_DIR,
        source_name
    )

    os.makedirs(
        cleaned_source_dir,
        exist_ok=True
    )

    cleaned_file = os.path.join(
        cleaned_source_dir,
        filename
    )

    print(
        f"Processing: {source_name}/{filename}"
    )

    try:

        with open(
            raw_file,
            "r",
            encoding="utf-8"
        ) as file:

            raw_text = file.read()

        cleaned_text = clean_text(
            raw_text
        )

        with open(
            cleaned_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                cleaned_text
            )

        print(
            f"Characters: "
            f"{len(raw_text)} -> "
            f"{len(cleaned_text)}"
        )

        print(
            f"Saved: {cleaned_file}"
        )

        return True

    except Exception as error:

        print(
            f"Error processing {filename}: "
            f"{error}"
        )

        return False


# ============================================================
# PROCESS SOURCE
# ============================================================

def process_source(source_name):
    """
    Process all .txt files belonging to one legal source.
    """

    source_dir = os.path.join(
        RAW_DATA_DIR,
        source_name
    )

    if not os.path.exists(source_dir):

        print(
            f"Source folder not found: "
            f"{source_name}"
        )

        return 0, 0

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
            f"No documents found for: "
            f"{source_name}"
        )

        return 0, 0

    print()
    print("=" * 70)

    print(
        f"SOURCE: {source_name.upper()}"
    )

    print("=" * 70)

    print(
        f"Documents found: {len(files)}"
    )

    successful = 0

    failed = 0

    for filename in sorted(files):

        result = process_file(
            source_name,
            filename
        )

        if result:
            successful += 1

        else:
            failed += 1

        print()

    return successful, failed


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LAWMATE AI - LEGAL DATA CLEANING")
    print("=" * 70)

    total_successful = 0

    total_failed = 0

    for source_name in SOURCE_FOLDERS:

        successful, failed = process_source(
            source_name
        )

        total_successful += successful
        total_failed += failed

    print()
    print("=" * 70)
    print("LEGAL DATA CLEANING COMPLETE")
    print("=" * 70)

    print(
        f"Successfully cleaned: "
        f"{total_successful}"
    )

    print(
        f"Failed: {total_failed}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
