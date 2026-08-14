import os
import re
from pypdf import PdfReader


# ============================================================
# LAWMATE AI - GAZETTE PDF IMPORTER
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

GAZETTE_DOCUMENTS = [
    {
        "pdf_file": "001_bns_amendment_2024.pdf",
        "title": "Bharatiya Nyaya Sanhita (Amendment) Act, 2024",
        "gazette_id": "CG-DL-E-03082024-256016",
        "publication_date": "03-08-2024",
        "source_url": (
            "https://egazette.gov.in/"
            "WriteReadData/2024/256016.pdf"
        ),
    },
    {
        "pdf_file": "002_dpdp_notification_2025.pdf",
        "title": (
            "Digital Personal Data Protection Act, 2023 "
            "- Gazette Notification"
        ),
        "gazette_id": "CG-DL-E-14112025-267647",
        "publication_date": "14-11-2025",
        "source_url": (
            "https://egazette.gov.in/"
            "WriteReadData/2025/267647.pdf"
        ),
    },
    {
        "pdf_file": "003_it_rules_amendment_2026.pdf",
        "title": (
            "Information Technology "
            "(Intermediary Guidelines and Digital Media "
            "Ethics Code) Amendment Rules, 2026"
        ),
        "gazette_id": "CG-DL-E-10022026-269993",
        "publication_date": "10-02-2026",
        "source_url": (
            "https://egazette.gov.in/"
            "WriteReadData/2026/269993.pdf"
        ),
    },
    {
        "pdf_file": "004_online_gaming_rules_2026.pdf",
        "title": (
            "Promotion and Regulation of "
            "Online Gaming Rules, 2026"
        ),
        "gazette_id": "CG-DL-E-22042026-271974",
        "publication_date": "22-04-2026",
        "source_url": (
            "https://egazette.gov.in/"
            "WriteReadData/2026/271974.pdf"
        ),
    },
    {
        "pdf_file": "005_electronic_evidence_rules_2025.pdf",
        "title": (
            "Electronic Evidence and "
            "Video Conferencing Rules, 2025"
        ),
        "gazette_id": "OFFICIAL-GAZETTE-264484",
        "publication_date": "2025",
        "source_url": (
            "https://egazette.gov.in/"
            "WriteReadData/2025/264484.pdf"
        ),
    },
]


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

PDF_FOLDER = os.path.join(
    BASE_DIR,
    "source_pdfs",
    "gazette"
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "raw_data",
    "gazette"
)

os.makedirs(
    PDF_FOLDER,
    exist_ok=True
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


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
# EXTRACT PDF
# ============================================================

def extract_pdf_text(filepath):

    reader = PdfReader(
        filepath
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

    return normalize_text(
        "\n\n".join(pages)
    )


# ============================================================
# SAVE TEXT
# ============================================================

def save_document(
    index,
    document,
    text
):

    filename = (
        f"{index:03d}_"
        f"{safe_filename(document['title'])}.txt"
    )

    filepath = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    metadata = (
        "SOURCE: Gazette of India\n"
        "SOURCE_TYPE: Gazette Document\n"
        f"TITLE: {document['title']}\n"
        f"GAZETTE_ID: {document['gazette_id']}\n"
        f"PUBLICATION_DATE: "
        f"{document['publication_date']}\n"
        f"URL: {document['source_url']}\n"
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
        "LAWMATE AI - GAZETTE PDF IMPORTER"
    )
    print("=" * 70)

    print(
        f"\nExpected Gazette PDFs: "
        f"{len(GAZETTE_DOCUMENTS)}"
    )

    print(
        f"PDF input folder: "
        f"{PDF_FOLDER}"
    )

    print(
        f"Output folder: "
        f"{OUTPUT_FOLDER}"
    )

    successful = 0
    failed = 0
    missing = 0

    for index, document in enumerate(
        GAZETTE_DOCUMENTS,
        start=1
    ):

        print()
        print("-" * 70)

        print(
            f"[{index}/"
            f"{len(GAZETTE_DOCUMENTS)}]"
        )

        print(
            f"Title: "
            f"{document['title']}"
        )

        pdf_path = os.path.join(
            PDF_FOLDER,
            document["pdf_file"]
        )

        if not os.path.exists(
            pdf_path
        ):

            print(
                f"Missing PDF: "
                f"{document['pdf_file']}"
            )

            missing += 1
            continue

        try:

            print(
                "Extracting Gazette PDF..."
            )

            text = extract_pdf_text(
                pdf_path
            )

            if len(text) < 500:

                print(
                    "Warning: extracted text "
                    "is unexpectedly short."
                )

                failed += 1
                continue

            filepath = save_document(
                index,
                document,
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
        "GAZETTE IMPORT COMPLETE"
    )
    print("=" * 70)

    print(
        f"Successful: {successful}"
    )

    print(
        f"Missing PDFs: {missing}"
    )

    print(
        f"Failed: {failed}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()