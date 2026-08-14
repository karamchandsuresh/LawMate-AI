import os
import re
from io import BytesIO

import requests
from pypdf import PdfReader


# ============================================================
# TARGET JUDGMENTS
# ============================================================

TARGET_JUDGMENTS = [
    {
        "court": "High Court of Delhi",
        "case_title": (
            "Indian Renewable Energy Development Agency Limited "
            "v Chhattisgarh State Power Distribution Co. Ltd. & Ors."
        ),
        "date": "09-10-2025",
        "url": (
            "https://delhihighcourt.nic.in/app/showFileJudgment/"
            "68309102025LPA4342025_163226.pdf"
        ),
    },
    {
        "court": "High Court of Delhi",
        "case_title": (
            "Mohd. Zuhaib v State of NCT of Delhi and Anr."
        ),
        "date": "17-01-2026",
        "url": (
            "https://delhihighcourt.nic.in/app/showFileJudgment/"
            "AJB17012026BA49382025_144906.pdf"
        ),
    },
    {
        "court": "High Court of Delhi",
        "case_title": (
            "M/S Jasmeet Trading Company v Additional Commissioner, "
            "CGST, Delhi North"
        ),
        "date": "30-05-2025",
        "url": (
            "https://delhihighcourt.nic.in/app/showFileJudgment/"
            "PMS30052025CW80322025_174204.pdf"
        ),
    },
    {
        "court": "High Court of Delhi",
        "case_title": (
            "Electro Mech Engineers v Nishant Promoters Pvt. Ltd."
        ),
        "date": "11-12-2025",
        "url": (
            "https://delhihighcourt.nic.in/app/showFileJudgment/"
            "68011122025FAOC2322024_171840.pdf"
        ),
    },
    {
        "court": "High Court of Delhi",
        "case_title": (
            "Saumya Chaurasia v Union of India & Others"
        ),
        "date": "08-12-2025",
        "url": (
            "https://delhihighcourt.nic.in/app/showFileJudgment/"
            "VKR08122025CW81912025_181729.pdf"
        ),
    },
    {
        "court": "High Court of Delhi",
        "case_title": (
            "Ranjana Rajagopalan v Lt. Governor of Delhi & Ors."
        ),
        "date": "16-12-2025",
        "url": (
            "https://delhihighcourt.nic.in/app/showFileJudgment/"
            "NAC16122025CW43322021_174340.pdf"
        ),
    },
    {
        "court": "High Court of Delhi",
        "case_title": (
            "Rajan & Ors. v Govt. of NCT of Delhi & Anr."
        ),
        "date": "08-12-2025",
        "url": (
            "https://delhihighcourt.nic.in/app/showFileJudgment/"
            "61708122025CRLMM70332025_104107.pdf"
        ),
    },
    {
        "court": "High Court of Delhi",
        "case_title": (
            "Joginder v State (NCT of Delhi)"
        ),
        "date": "09-12-2025",
        "url": (
            "https://delhihighcourt.nic.in/app/showFileJudgment/"
            "68909122025CRLA2282004_163627.pdf"
        ),
    },
]


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "raw_data",
    "high_court"
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
# SAFE FILE NAME
# ============================================================

def safe_filename(text):

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

    return text[:130]


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
        response.content.startswith(b"%PDF")
        or "application/pdf" in content_type
    )

    if not is_pdf:
        raise ValueError(
            "Downloaded content is not a valid PDF."
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

        except Exception as error:

            print(
                f"Warning: page {page_number} "
                f"could not be extracted: {error}"
            )

            continue

        if text and text.strip():

            pages.append(
                f"--- PAGE {page_number} ---\n"
                f"{text.strip()}"
            )

    return "\n\n".join(
        pages
    ).strip()


# ============================================================
# VALIDATE JUDGMENT RECORD
# ============================================================

def validate_judgment(judgment):

    required_fields = [
        "court",
        "case_title",
        "date",
        "url",
    ]

    for field in required_fields:

        if field not in judgment:
            raise ValueError(
                f"Missing field: {field}"
            )

        if not str(
            judgment[field]
        ).strip():

            raise ValueError(
                f"Empty field: {field}"
            )


# ============================================================
# SAVE JUDGMENT
# ============================================================

def save_judgment(
    index,
    judgment,
    text
):

    filename = (
        f"{index:03d}_"
        f"{safe_filename(judgment['case_title'])}.txt"
    )

    filepath = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    metadata = (
        "SOURCE: High Court of Delhi\n"
        "SOURCE_TYPE: High Court Judgment\n"
        f"COURT: {judgment['court']}\n"
        f"CASE_TITLE: {judgment['case_title']}\n"
        f"JUDGMENT_DATE: {judgment['date']}\n"
        f"URL: {judgment['url']}\n"
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
        "LAWMATE AI - HIGH COURT JUDGMENT IMPORTER"
    )
    print("=" * 70)

    print(
        f"\nTarget judgments: "
        f"{len(TARGET_JUDGMENTS)}"
    )

    print(
        f"Output folder: "
        f"{OUTPUT_FOLDER}"
    )

    successful = 0
    failed = 0

    for index, judgment in enumerate(
        TARGET_JUDGMENTS,
        start=1
    ):

        print()
        print("-" * 70)

        print(
            f"[{index}/"
            f"{len(TARGET_JUDGMENTS)}]"
        )

        try:

            validate_judgment(
                judgment
            )

            print(
                f"Court: "
                f"{judgment['court']}"
            )

            print(
                f"Case: "
                f"{judgment['case_title']}"
            )

            print(
                f"Date: "
                f"{judgment['date']}"
            )

            print(
                "Downloading judgment PDF..."
            )

            pdf_bytes = download_pdf(
                judgment["url"]
            )

            print(
                f"Downloaded: "
                f"{len(pdf_bytes):,} bytes"
            )

            print(
                "Extracting judgment text..."
            )

            text = extract_pdf_text(
                pdf_bytes
            )

            if len(text) < 1000:

                print(
                    "Warning: extracted text "
                    "is unexpectedly short."
                )

                failed += 1
                continue

            filepath = save_judgment(
                index,
                judgment,
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

        except Exception as error:

            print(
                f"Failed: {error}"
            )

            failed += 1

    print()
    print("=" * 70)
    print(
        "HIGH COURT IMPORT COMPLETE"
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