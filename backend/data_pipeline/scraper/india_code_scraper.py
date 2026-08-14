import os
import time
import requests
from bs4 import BeautifulSoup


# ============================================================
# INDIA CODE TARGET DOCUMENTS
# ============================================================

TARGET_ACTS = [
    {
        "title": "Bharatiya Nyaya Sanhita, 2023",
        "url": "https://www.indiacode.nic.in/handle/123456789/20062",
    },
    {
        "title": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "url": "https://www.indiacode.nic.in/handle/123456789/20099",
    },
    {
        "title": "Bharatiya Sakshya Adhiniyam, 2023",
        "url": "https://www.indiacode.nic.in/handle/123456789/20063",
    },
    {
        "title": "Consumer Protection Act, 2019",
        "url": "https://www.indiacode.nic.in/handle/123456789/15256",
    },
    {
        "title": "Information Technology Act, 2000",
        "url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },
    {
        "title": "Right to Information Act, 2005",
        "url": "https://www.indiacode.nic.in/handle/123456789/2065",
    },
    {
        "title": "Protection of Women from Domestic Violence Act, 2005",
        "url": "https://www.indiacode.nic.in/handle/123456789/2021",
    },
    {
        "title": "Indian Contract Act, 1872",
        "url": "https://www.indiacode.nic.in/handle/123456789/2187",
    },
    {
        "title": "Motor Vehicles Act, 1988",
        "url": "https://www.indiacode.nic.in/handle/123456789/1798",
    },
    {
        "title": "Specific Relief Act, 1963",
        "url": "https://www.indiacode.nic.in/handle/123456789/1583",
    },
    {
        "title": (
            "Aadhaar (Targeted Delivery of Financial and Other "
            "Subsidies, Benefits and Services) Act, 2016"
        ),
        "url": "https://www.indiacode.nic.in/handle/123456789/2160",
    },
    {
        "title": "Protection of Children from Sexual Offences Act, 2012",
        "url": "https://www.indiacode.nic.in/handle/123456789/2079",
    },
    {
        "title": (
            "Sexual Harassment of Women at Workplace "
            "(Prevention, Prohibition and Redressal) Act, 2013"
        ),
        "url": "https://www.indiacode.nic.in/handle/123456789/2104",
    },
    {
        "title": "Legal Services Authorities Act, 1987",
        "url": "https://www.indiacode.nic.in/handle/123456789/1925",
    },
    {
        "title": "Arbitration and Conciliation Act, 1996",
        "url": "https://www.indiacode.nic.in/handle/123456789/1978",
    },
    {
        "title": "Hindu Marriage Act, 1955",
        "url": "https://www.indiacode.nic.in/handle/123456789/1560",
    },
    {
        "title": "Limitation Act, 1963",
        "url": "https://www.indiacode.nic.in/handle/123456789/1565",
    },
    {
        "title": "Companies Act, 2013",
        "url": "https://www.indiacode.nic.in/handle/123456789/2114",
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
    "india_code"
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
    Download an India Code webpage using UTF-8.
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
# SAFE FILE NAME
# ============================================================

def safe_filename(title):
    """
    Convert a legal title into a Windows-safe filename.
    """

    allowed = []

    for character in title:

        if character.isalnum() or character in " _-":
            allowed.append(character)

        else:
            allowed.append("_")

    filename = "".join(allowed)

    filename = " ".join(
        filename.split()
    )

    return filename[:140]


# ============================================================
# EXTRACT ACT TEXT
# ============================================================

def extract_act_text(html):
    """
    Extract readable Act text from India Code.
    """

    soup = BeautifulSoup(
        html,
        "lxml"
    )

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

    text = soup.get_text(
        separator="\n",
        strip=True
    )

    lines = []

    previous_line = None

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line == previous_line:
            continue

        lines.append(line)

        previous_line = line

    return "\n".join(lines)


# ============================================================
# SAVE DOCUMENT
# ============================================================

def save_document(
    index,
    title,
    url,
    content
):
    """
    Save one India Code Act as UTF-8 text.
    """

    filename = (
        f"{index:03d}_"
        f"{safe_filename(title)}.txt"
    )

    filepath = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    metadata = (
        "SOURCE: India Code\n"
        f"TITLE: {title}\n"
        f"URL: {url}\n"
        f"{'=' * 80}\n\n"
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(metadata)
        file.write(content)

    return filepath


# ============================================================
# VALIDATE PAGE
# ============================================================

def validate_act_page(
    title,
    content
):
    """
    Perform simple checks before saving a legal Act.
    """

    if len(content) < 500:
        return False

    title_words = [
        word.lower()
        for word in title.split()
        if len(word) >= 4
    ]

    content_lower = content.lower()

    matches = sum(
        1
        for word in title_words
        if word in content_lower
    )

    if title_words and matches < max(
        1,
        len(title_words) // 3
    ):
        return False

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LAWMATE AI - INDIA CODE SCRAPER")
    print("=" * 70)

    print(
        f"\nTarget Acts: {len(TARGET_ACTS)}"
    )

    successful = 0
    failed = 0

    for index, act in enumerate(
        TARGET_ACTS,
        start=1
    ):

        title = act["title"]
        url = act["url"]

        print()
        print("-" * 70)

        print(
            f"[{index}/{len(TARGET_ACTS)}]"
        )

        print(
            f"Scraping: {title}"
        )

        print(
            f"URL: {url}"
        )

        try:

            html = get_page(
                url
            )

            content = extract_act_text(
                html
            )

            if not validate_act_page(
                title,
                content
            ):

                print(
                    "Validation failed: "
                    "page content does not look "
                    "like the expected Act."
                )

                failed += 1

                continue

            filepath = save_document(
                index,
                title,
                url,
                content
            )

            print(
                f"Saved: {filepath}"
            )

            print(
                f"Characters: "
                f"{len(content)}"
            )

            successful += 1

            # Avoid aggressive requests
            time.sleep(1)

        except requests.RequestException as error:

            print(
                f"Request failed: "
                f"{error}"
            )

            failed += 1

        except Exception as error:

            print(
                f"Unexpected error: "
                f"{error}"
            )

            failed += 1

    print()
    print("=" * 70)
    print("INDIA CODE SCRAPING COMPLETE")
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