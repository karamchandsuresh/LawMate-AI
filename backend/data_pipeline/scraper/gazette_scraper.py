import os
import re
import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_URL = "https://egazette.gov.in/?acceptscookies=yes"

MAX_DOCUMENTS = 10


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "raw_data",
    "gazette"
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ============================================================
# REQUEST CONFIGURATION
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/120 Safari/537.36 "
        "LawMate-AI/1.0"
    )
}


# ============================================================
# DOWNLOAD PAGE
# ============================================================

def get_page(url):
    """
    Download the official eGazette homepage.
    """

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    response.encoding = "utf-8"

    return response.text


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):
    """
    Remove excessive whitespace.
    """

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SAFE FILE NAME
# ============================================================

def safe_filename(text):
    """
    Convert Gazette ID into a safe filename.
    """

    text = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        text
    )

    return text[:120]


# ============================================================
# EXTRACT GAZETTE RECORDS
# ============================================================

def extract_records(html):
    """
    Extract recent Gazette metadata from the
    official eGazette homepage.
    """

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    text = soup.get_text(
        separator="\n",
        strip=True
    )

    lines = [
        normalize_text(line)
        for line in text.splitlines()
        if normalize_text(line)
    ]

    records = []

    # Gazette IDs generally look similar to:
    #
    # CG-DL-E-30072026-274980
    # CG-DL-W-30072026-274965
    #
    # We locate Gazette IDs and use surrounding
    # lines as official metadata.

    gazette_pattern = re.compile(
        r"^[A-Z]{2}-[A-Z]{2}-[A-Z]-"
        r"\d{8}-\d+$"
    )

    for index, line in enumerate(lines):

        if not gazette_pattern.match(line):
            continue

        gazette_id = line

        previous_lines = lines[
            max(0, index - 4):index
        ]

        # Avoid duplicate Gazette IDs
        if any(
            record["gazette_id"] == gazette_id
            for record in records
        ):
            continue

        context = " | ".join(
            previous_lines
        )

        records.append(
            {
                "gazette_id": gazette_id,
                "context": context
            }
        )

    return records


# ============================================================
# SAVE RECORD
# ============================================================

def save_record(index, record):
    """
    Save one Gazette metadata record.
    """

    gazette_id = record[
        "gazette_id"
    ]

    filename = (
        f"{index:03d}_"
        f"{safe_filename(gazette_id)}.txt"
    )

    filepath = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    content = (
        "SOURCE: Gazette of India\n"
        "SOURCE_TYPE: Gazette Notification Metadata\n"
        f"GAZETTE_ID: {gazette_id}\n"
        f"SOURCE_URL: {SOURCE_URL}\n"
        f"{'=' * 80}\n\n"
        "OFFICIAL GAZETTE METADATA:\n"
        f"{record['context']}\n"
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(content)

    return filepath


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LAWMATE AI - GAZETTE OF INDIA SCRAPER")
    print("=" * 70)

    print(
        f"\nSource: {SOURCE_URL}"
    )

    try:

        html = get_page(
            SOURCE_URL
        )

    except requests.RequestException as error:

        print(
            f"Failed to access eGazette: "
            f"{error}"
        )

        return

    records = extract_records(
        html
    )

    print(
        f"\nGazette records found: "
        f"{len(records)}"
    )

    if not records:

        print(
            "No Gazette records were extracted."
        )

        return

    selected_records = records[
        :MAX_DOCUMENTS
    ]

    print(
        f"Saving first "
        f"{len(selected_records)} records..."
    )

    successful = 0
    failed = 0

    for index, record in enumerate(
        selected_records,
        start=1
    ):

        print()
        print("-" * 70)

        try:

            print(
                f"[{index}/"
                f"{len(selected_records)}]"
            )

            print(
                f"Gazette ID: "
                f"{record['gazette_id']}"
            )

            filepath = save_record(
                index,
                record
            )

            print(
                f"Saved: {filepath}"
            )

            successful += 1

        except Exception as error:

            print(
                f"Failed: {error}"
            )

            failed += 1

    print()
    print("=" * 70)
    print("GAZETTE SCRAPING COMPLETE")
    print("=" * 70)

    print(
        f"Successful: {successful}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        f"Output folder: "
        f"{OUTPUT_FOLDER}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()