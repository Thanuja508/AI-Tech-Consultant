import asyncio
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import httpx


SITEMAP_URL = (
    "https://support.brilliantdirectories.com/support/sitemap.xml"
)

# Save files in the project's data folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SITEMAP_FILE = DATA_DIR / "sitemap_urls.json"


async def download_sitemap():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    headers = {
        "User-Agent": "AI-Tech-Consultant-Student-Project/1.0"
    }

    try:
        async with httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            follow_redirects=True,
        ) as client:
            response = await client.get(SITEMAP_URL)
            response.raise_for_status()

        root = ET.fromstring(response.content)

        urls = sorted({
            element.text.strip()
            for element in root.iter()
            if element.tag.endswith("loc")
            and element.text
            and element.text.strip().startswith("http")
        })

        if not urls:
            print("No URLs found. Check the sitemap format.")
            return

        SITEMAP_FILE.write_text(
            json.dumps(urls, indent=2),
            encoding="utf-8",
        )

        print(f"Successfully saved {len(urls)} sitemap URLs.")
        print(f"Saved to: {SITEMAP_FILE}")

    except (httpx.HTTPError, ET.ParseError, OSError) as error:
        print(f"Could not download the sitemap: {error}")


if __name__ == "__main__":
    asyncio.run(download_sitemap())