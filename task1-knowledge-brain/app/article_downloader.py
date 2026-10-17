import asyncio
import json
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
URLS_FILE = DATA_DIR / "sitemap_urls.json"
ARTICLES_DIR = DATA_DIR / "articles"

BATCH_SIZE = 5
DELAY_SECONDS = 1.0
TIMEOUT_SECONDS = 30


async def download_article(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
) -> dict | None:
    async with semaphore:
        try:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for element in soup(
                ["script", "style", "nav", "footer", "header"]
            ):
                element.decompose()

            title = soup.title.get_text(" ", strip=True) if soup.title else url

            content = soup.select_one(
                "main, article, .article-body, .content"
            )

            if content is None:
                content = soup.body or soup

            text = content.get_text(" ", strip=True)
            text = re.sub(r"\s+", " ", text).strip()

            images = []
            for image in content.find_all("img"):
                src = image.get("src") or image.get("data-src")
                if src:
                    images.append({
                        "url": str(response.url.join(
                            httpx.URL(src)
                        )),
                        "alt": image.get("alt", ""),
                    })

            return {
                "url": url,
                "title": title,
                "content": text,
                "images": images,
                "status": "success",
            }

        except (httpx.HTTPError, ValueError) as error:
            print(f"Failed: {url} — {error}")
            return {
                "url": url,
                "status": "failed",
                "error": str(error),
            }


async def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    if not URLS_FILE.exists():
        print(f"Sitemap file not found: {URLS_FILE}")
        return

    with URLS_FILE.open("r", encoding="utf-8") as file:
        urls = json.load(file)

    if not isinstance(urls, list):
        print("The sitemap JSON must contain a list of URLs.")
        return

    urls = [
        url for url in urls
        if isinstance(url, str)
        and url.startswith("https://support.brilliantdirectories.com/")
        and "/support/solutions/articles/" in url
    ]

    print(f"Found {len(urls)} article URLs.")

    semaphore = asyncio.Semaphore(BATCH_SIZE)
    timeout = httpx.Timeout(TIMEOUT_SECONDS)

    results = []

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": "AI-Tech-Consultant-Student-Project/1.0"},
    ) as client:
        for start in range(0, len(urls), BATCH_SIZE):
            batch = urls[start:start + BATCH_SIZE]

            batch_results = await asyncio.gather(
                *[
                    download_article(client, url, semaphore)
                    for url in batch
                ]
            )

            results.extend(batch_results)

            successful = sum(
                item is not None and item["status"] == "success"
                for item in batch_results
            )

            print(
                f"Progress: {min(start + len(batch), len(urls))}"
                f"/{len(urls)} URLs checked; "
                f"{successful} succeeded in this batch."
            )

            checkpoint = {
                "processed": len(results),
                "results": results,
            }

            (DATA_DIR / "download_checkpoint.json").write_text(
                json.dumps(checkpoint, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            if start + BATCH_SIZE < len(urls):
                await asyncio.sleep(DELAY_SECONDS)

    saved = 0

    for item in results:
        if item["status"] != "success":
            continue

        filename = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            item["url"].rstrip("/").split("/")[-1],
        )

        if not filename:
            filename = f"article_{saved}"

        output_file = ARTICLES_DIR / f"{filename}.json"
        output_file.write_text(
            json.dumps(item, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        saved += 1

    print(f"\nFinished. Saved {saved} articles to {ARTICLES_DIR}")
    print(f"Checkpoint: {DATA_DIR / 'download_checkpoint.json'}")


if __name__ == "__main__":
    asyncio.run(main())