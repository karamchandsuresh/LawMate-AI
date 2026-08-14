import os
import re
import time
import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_URL = (
    "https://www.sci.gov.in/"
    "landmark-judgment-summaries/"
)

MAX_SUMMARIES = 12


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "raw_data",
    "supreme_court"
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
    Download the Supreme Court webpage.
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
# SAFE FILENAME
# ============================================================

def safe_filename(text):
    """
    Convert case title into a Windows-safe filename.
    """

    text = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text[:120]


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):
    """
    Clean basic whitespace from extracted text.
    """

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# EXTRACT SUMMARY BLOCKS
# ============================================================

def extract_summaries(html):
    """
    Extract Supreme Court landmark judgment summaries
    from the official summaries page.
    """

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    # Remove non-content elements
    for element in soup(
        [
            "script",
            "style",
            "noscript",
            "nav",
            "footer",
        ]
    ):
        element.decompose()

    page_text = soup.get_text(
        separator="\n",
        strip=True
    )

    page_text = normalize_text(
        page_text
    )

    # The official page lists landmark summaries using
    # serial-numbered entries.
    #
    # We split using patterns such as:
    #
    # 1
    # 02-07-2026
    # CASE TITLE
    #
    # This keeps the full summary text for each entry.

    pattern = (
        r"(?ms)"
        r"(?:^|\n)"
        r"(\d+)\n"
        r"(\d{2}-\d{2}-\d{4})\n"
        r"(.*?)"
        r"(?="
        r"\n\d+\n\d{2}-\d{2}-\d{4}\n"
        r"|\Z"
        r")"
    )

    matches = re.findall(
        pattern,
        page_text
    )

    summaries = []

    for serial, date, content in matches:

        content = content.strip()

        if len(content) < 300:
            continue

        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        case_title = lines[0]

        summaries.append(
            {
                "serial": serial,
                "date": date,
                "case_title": case_title,
                "content": content
            }
        )

    return summaries


# ============================================================
# SAVE SUMMARY
# ============================================================

def save_summary(
    index,
    summary
):
    """
    Save one Supreme Court judgment summary.
    """

    case_title = summary[
        "case_title"
    ]

    filename = (
        f"{index:03d}_"
        f"{safe_filename(case_title)}.txt"
    )

    filepath = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    metadata = (
        "SOURCE: Supreme Court of India\n"
        "SOURCE_TYPE: Landmark Judgment Summary\n"
        f"CASE_TITLE: {case_title}\n"
        f"JUDGMENT_DATE: {summary['date']}\n"
        f"URL: {SOURCE_URL}\n"
        "NOTE: This is an official Supreme Court "
        "judgment summary and is not itself part "
        "of the Court's judgment or reasons.\n"
        f"{'=' * 80}\n\n"
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            metadata
        )

        file.write(
            summary["content"]
        )

    return filepath


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LAWMATE AI - SUPREME COURT SCRAPER")
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
            f"Failed to download Supreme Court page: "
            f"{error}"
        )

        return

    summaries = extract_summaries(
        html
    )

    print(
        f"\nJudgment summaries found: "
        f"{len(summaries)}"
    )

    if not summaries:

        print(
            "No judgment summaries were extracted."
        )

        return

    selected = summaries[
        :MAX_SUMMARIES
    ]

    print(
        f"Saving first "
        f"{len(selected)} summaries..."
    )

    successful = 0
    failed = 0

    for index, summary in enumerate(
        selected,
        start=1
    ):

        try:

            print()
            print("-" * 70)

            print(
                f"[{index}/{len(selected)}]"
            )

            print(
                f"Case: "
                f"{summary['case_title']}"
            )

            filepath = save_summary(
                index,
                summary
            )

            print(
                f"Saved: {filepath}"
            )

            print(
                f"Characters: "
                f"{len(summary['content'])}"
            )

            successful += 1

            time.sleep(
                0.25
            )

        except Exception as error:

            print(
                f"Error saving summary: "
                f"{error}"
            )

            failed += 1

    print()
    print("=" * 70)
    print("SUPREME COURT SCRAPING COMPLETE")
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