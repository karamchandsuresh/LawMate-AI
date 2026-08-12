import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://www.indiacode.nic.in"

BROWSE_URL = (
    "https://www.indiacode.nic.in/"
    "handle/123456789/1362/browse"
    "?type=shorttitle&sort_by=3&order=ASC"
    "&rpp=20&etal=-1&null="
)

OUTPUT_FOLDER = os.path.join(
    os.path.dirname(__file__),
    "..",
    "raw_data"
)

HEADERS = {
    "User-Agent": "LawMate-AI/1.0"
}


def get_page(url):
    """Download a webpage."""

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def find_act_links(html, page_url):
    """Find individual Act pages from an India Code browse page."""

    soup = BeautifulSoup(html, "lxml")

    act_links = []

    for link in soup.find_all("a", href=True):

        href = link["href"]

        text = link.get_text(" ", strip=True)

        # Individual Act pages use /handle/... followed by ?view_type=browse
        if "/handle/123456789/" in href and "view_type=browse" in href:

            full_url = urljoin(page_url, href)

            if full_url not in act_links:

                act_links.append(full_url)

    return act_links


def extract_act_content(html):
    """Extract readable text from an individual Act page."""

    soup = BeautifulSoup(html, "lxml")

    # Remove elements that are not useful legal content
    for element in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer"
    ]):
        element.decompose()

    text = soup.get_text(
        "\n",
        strip=True
    )

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def save_act(title, content, index):
    """Save one Act into raw_data."""

    safe_title = "".join(
        character if character.isalnum() or character in " _-" else "_"
        for character in title
    )

    safe_title = safe_title[:100].strip()

    if not safe_title:
        safe_title = f"act_{index}"

    filename = f"{index:03d}_{safe_title}.txt"

    filepath = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(content)

    return filepath


def main():

    print("Connecting to India Code...")

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    # --------------------------------------------------
    # STEP 1: Download browse page
    # --------------------------------------------------

    browse_html = get_page(BROWSE_URL)

    print("India Code browse page loaded.")

    # --------------------------------------------------
    # STEP 2: Find Act links
    # --------------------------------------------------

    act_links = find_act_links(
        browse_html,
        BROWSE_URL
    )

    print(f"Individual Act links found: {len(act_links)}")

    if not act_links:

        print("No Act links were found.")

        return

    # --------------------------------------------------
    # STEP 3: Scrape Acts
    # --------------------------------------------------

    # Version 1 test:
    # Scrape only the first 5 Acts.
    #
    # Once this works correctly, we can increase
    # the number without changing the pipeline.

    test_links = act_links[:5]

    print(
        f"Testing with {len(test_links)} Acts..."
    )

    for index, act_url in enumerate(
        test_links,
        start=1
    ):

        try:

            print()
            print(
                f"[{index}/{len(test_links)}] "
                f"Scraping:"
            )

            print(act_url)

            act_html = get_page(act_url)

            act_text = extract_act_content(
                act_html
            )

            if len(act_text) < 500:

                print(
                    "Warning: very little text "
                    "was extracted."
                )

                continue

            # Try to identify a useful title
            soup = BeautifulSoup(
                act_html,
                "lxml"
            )

            title = soup.title.get_text(
                " ",
                strip=True
            ) if soup.title else f"Act {index}"

            filepath = save_act(
                title,
                act_text,
                index
            )

            print(
                f"Saved: {filepath}"
            )

            print(
                f"Characters: {len(act_text)}"
            )

            # Be polite to the website
            time.sleep(1)

        except Exception as error:

            print(
                f"Error scraping Act {index}: "
                f"{error}"
            )

    print()
    print("India Code scraping test completed.")
    print(
        f"Raw files saved in: {OUTPUT_FOLDER}"
    )


if __name__ == "__main__":
    main()