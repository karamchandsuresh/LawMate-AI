import os
import re
import time
from io import BytesIO
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader


# ============================================================
# CONFIGURATION
# ============================================================

REPORTS_PAGE = (
    "https://lawcommissionofindia.nic.in/"
    "report_twentysecond/"
)

TARGET_REPORTS = {
    "282",
    "283",
    "284",
    "285",
    "287",
}


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "raw_data",
    "law_commission"
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
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    response.encoding = response.apparent_encoding

    return response.text


# ============================================================
# SAFE FILE NAME
# ============================================================

def safe_filename(text):
    text = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        text
    )

    text = " ".join(
        text.split()
    )

    return text[:130]


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):
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
        r"\n\s*\n\s*\n+",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# FIND SELECTED REPORT LINKS
# ============================================================

def find_report_links(html):
    """
    Parse the official Law Commission table.

    Each row contains:
    report number | subject | date | PDF link
    """

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    reports = []

    seen_numbers = set()

    for row in soup.find_all("tr"):

        cells = row.find_all(
            ["td", "th"]
        )

        if len(cells) < 4:
            continue

        report_number = cells[0].get_text(
            " ",
            strip=True
        )

        # Keep only our selected reports
        if report_number not in TARGET_REPORTS:
            continue

        subject = cells[1].get_text(
            " ",
            strip=True
        )

        submission_date = cells[2].get_text(
            " ",
            strip=True
        )

        pdf_link = cells[3].find(
            "a",
            href=True
        )

        if not pdf_link:
            continue

        pdf_url = urljoin(
            REPORTS_PAGE,
            pdf_link["href"]
        )

        if report_number in seen_numbers:
            continue

        seen_numbers.add(
            report_number
        )

        reports.append(
            {
                "report_number": report_number,
                "title": subject,
                "submission_date": submission_date,
                "url": pdf_url,
            }
        )

    return reports


# ============================================================
# DOWNLOAD PDF
# ============================================================

def download_pdf(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=90
    )

    response.raise_for_status()

    content_type = response.headers.get(
        "Content-Type",
        ""
    ).lower()

    is_pdf = (
        "application/pdf" in content_type
        or response.content.startswith(
            b"%PDF"
        )
    )

    if not is_pdf:
        raise ValueError(
            "Downloaded content is not a PDF."
        )

    return response.content


# ============================================================
# EXTRACT PDF TEXT
# ============================================================

def extract_pdf_text(pdf_bytes):
    reader = PdfReader(
        BytesIO(pdf_bytes)
    )

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        try:

            text = page.extract_text()

            if text:

                pages.append(
                    f"\n--- PAGE {page_number} ---\n"
                    f"{text.strip()}"
                )

        except Exception as error:

            print(
                f"Warning: page "
                f"{page_number} extraction failed: "
                f"{error}"
            )

    return normalize_text(
        "\n".join(pages)
    )


# ============================================================
# SAVE REPORT
# ============================================================

def save_report(
    index,
    report,
    text
):
    report_number = report[
        "report_number"
    ]

    title = report[
        "title"
    ]

    filename = (
        f"{index:03d}_"
        f"Report_{report_number}_"
        f"{safe_filename(title)}.txt"
    )

    filepath = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    metadata = (
        "SOURCE: Law Commission of India\n"
        "SOURCE_TYPE: Law Commission Report\n"
        f"REPORT_NUMBER: {report_number}\n"
        f"TITLE: {title}\n"
        f"SUBMISSION_DATE: "
        f"{report['submission_date']}\n"
        f"URL: {report['url']}\n"
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
            text
        )

    return filepath


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "LAWMATE AI - LAW COMMISSION SCRAPER"
    )
    print("=" * 70)

    print(
        f"\nSource: {REPORTS_PAGE}"
    )

    print(
        "Target reports: "
        + ", ".join(
            sorted(TARGET_REPORTS)
        )
    )

    # --------------------------------------------------------
    # LOAD PAGE
    # --------------------------------------------------------

    try:

        print(
            "\nConnecting to Law Commission..."
        )

        html = get_page(
            REPORTS_PAGE
        )

        print(
            "Reports page loaded."
        )

    except requests.RequestException as error:

        print(
            f"Failed to access website: "
            f"{error}"
        )

        return

    # --------------------------------------------------------
    # FIND REPORTS
    # --------------------------------------------------------

    reports = find_report_links(
        html
    )

    print(
        f"\nTarget reports found: "
        f"{len(reports)}"
    )

    if not reports:

        print(
            "No selected report links found."
        )

        return

    reports.sort(
        key=lambda report: int(
            report["report_number"]
        )
    )

    successful = 0
    failed = 0

    # --------------------------------------------------------
    # DOWNLOAD + EXTRACT
    # --------------------------------------------------------

    for index, report in enumerate(
        reports,
        start=1
    ):

        print()
        print("-" * 70)

        print(
            f"[{index}/{len(reports)}]"
        )

        print(
            f"Report {report['report_number']}"
        )

        print(
            f"Title: {report['title']}"
        )

        print(
            f"URL: {report['url']}"
        )

        try:

            print(
                "Downloading PDF..."
            )

            pdf_bytes = download_pdf(
                report["url"]
            )

            print(
                f"Downloaded: "
                f"{len(pdf_bytes):,} bytes"
            )

            print(
                "Extracting text..."
            )

            text = extract_pdf_text(
                pdf_bytes
            )

            if len(text) < 1000:

                print(
                    "Warning: extracted text "
                    "is too short."
                )

                failed += 1
                continue

            filepath = save_report(
                index,
                report,
                text
            )

            print(
                f"Saved: {filepath}"
            )

            print(
                f"Characters extracted: "
                f"{len(text):,}"
            )

            successful += 1

            time.sleep(1)

        except Exception as error:

            print(
                f"Failed: {error}"
            )

            failed += 1

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "LAW COMMISSION SCRAPING COMPLETE"
    )
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