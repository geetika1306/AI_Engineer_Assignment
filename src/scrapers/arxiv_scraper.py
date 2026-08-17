import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import ssl
import certifi
import json
import os
import sys
from datetime import datetime, timezone


# Add src to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)


from utils.paper_metadata import (
    get_verified_github_info
)

from utils.checkpoint import (
    save_checkpoint
)

ARXIV_API_URL = "https://export.arxiv.org/api/query"


async def fetch_papers(
    session,
    start=0,
    max_results=20
):

    params = {
        "search_query": "cat:cs.AI",
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    async with session.get(
        ARXIV_API_URL,
        params=params
    ) as response:

        response.raise_for_status()

        return await response.text()


def parse_papers(xml_data):

    root = ET.fromstring(xml_data)

    namespace = {
        "atom": "http://www.w3.org/2005/Atom"
    }

    papers = []

    for entry in root.findall(
        "atom:entry",
        namespace
    ):

        title = entry.find(
            "atom:title",
            namespace
        )

        published = entry.find(
            "atom:published",
            namespace
        )

        paper_id = entry.find(
            "atom:id",
            namespace
        )

        summary = entry.find(
            "atom:summary",
            namespace
        )

        authors = []

        for author in entry.findall(
            "atom:author",
            namespace
        ):

            name = author.find(
                "atom:name",
                namespace
            )

            if name is not None:

                authors.append(
                    name.text.strip()
                )

        if (
            title is None
            or paper_id is None
        ):
            continue

        arxiv_url = paper_id.text.strip()

        # Extract arXiv ID
        arxiv_id = (
            arxiv_url
            .split("/abs/")[-1]
            .split("v")[0]
        )

        paper = {

            "schemaVersion": "1.0",

            "recordType": "RESEARCH_PAPER",

            "source": {
                "name": "arXiv",
                "url": arxiv_url
            },

            "content": {

                "title":
                    title.text.strip()
                    .replace("\n", " "),

                "authors":
                    authors,

                "paper_url":
                    arxiv_url,

                "arxiv_id":
                    arxiv_id,

                "summary":
                    (
                        summary.text.strip()
                        if summary is not None
                        else ""
                    ),

                "github_url":
                    None,

                "github_stars":
                    None,

                "published_date":
                    (
                        published.text.strip()
                        if published is not None
                        else None
                    )
            },

            "collectedAt":
                datetime.now(
                    timezone.utc
                ).isoformat()
        }

        papers.append(paper)

    return papers


def save_papers(
    papers,
    output_directory="data/raw"
):

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    output_file = os.path.join(
        output_directory,
        "research_papers.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            papers,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"\nSaved {len(papers)} papers to:"
        f"\n{output_file}"
    )


async def enrich_paper(
    session,
    paper,
    semaphore
):

    async with semaphore:

        arxiv_id = (
            paper["content"]
            ["arxiv_id"]
        )

        print(
            f"Checking GitHub: "
            f"{arxiv_id}"
        )

        try:

            github_info = await get_verified_github_info(
            session,
            arxiv_id
            )

            paper["content"][
                "github_url"
            ] = github_info[
                "github_url"
            ]

            paper["content"][
                "github_stars"
            ] = github_info[
                "github_stars"
            ]

        except Exception as error:

            print(
                f"GitHub lookup failed "
                f"for {arxiv_id}: {error}"
            )

        return paper


async def enrich_papers(
    session,
    papers
):

    # Limit concurrent API calls
    semaphore = asyncio.Semaphore(5)

    tasks = [
    enrich_paper(
        session,
        paper,
        semaphore
    )
    for paper in papers
]
    return await asyncio.gather(
        *tasks
    )


async def main():

    ssl_context = ssl.create_default_context(
        cafile=certifi.where()
    )

    connector = aiohttp.TCPConnector(
        ssl=ssl_context
    )

    async with aiohttp.ClientSession(
        connector=connector
    ) as session:

        print(
            "Fetching research papers "
            "from arXiv..."
        )

        # -----------------------------
        # CONFIGURATION
        # -----------------------------

        TOTAL_PAPERS = 1000
        BATCH_SIZE = 100

        all_papers = []

        # -----------------------------
        # PAGINATED ARXIV COLLECTION
        # -----------------------------

        for start in range(
            0,
            TOTAL_PAPERS,
            BATCH_SIZE
        ):

            print(
                f"\nFetching papers "
                f"{start + 1} - "
                f"{min(start + BATCH_SIZE, TOTAL_PAPERS)}"
            )

            try:

                xml_data = await fetch_papers(
                    session,
                    start=start,
                    max_results=BATCH_SIZE
                )

                papers = parse_papers(
                    xml_data
                )

                print(
                    f"Received {len(papers)} papers"
                )

                all_papers.extend(
                    papers
                )
                save_checkpoint(
                all_papers
                )
            except Exception as error:

                print(
                    f"Batch failed: {error}"
                )

                continue

            # Small delay between arXiv requests
            await asyncio.sleep(2)

        # -----------------------------
        # DEDUPLICATION
        # -----------------------------

        unique_papers = {}

        for paper in all_papers:

            arxiv_id = (
                paper["content"]
                ["arxiv_id"]
            )

            unique_papers[
                arxiv_id
            ] = paper

        papers = list(
            unique_papers.values()
        )

        print(
            f"\nTotal unique papers collected: "
            f"{len(papers)}"
        )

        # -----------------------------
        # GITHUB ENRICHMENT
        # -----------------------------

        print(
            "\nFinding verified GitHub "
            "repositories...\n"
        )

        papers = await enrich_papers(
            session,
            papers
        )

        # -----------------------------
        # SAVE
        # -----------------------------

        save_papers(
            papers
        )

        # -----------------------------
        # SUMMARY
        # -----------------------------

        github_count = sum(
            1
            for paper in papers
            if paper["content"][
                "github_url"
            ]
        )

        print(
            "\n========== SUMMARY =========="
        )

        print(
            f"Total papers: {len(papers)}"
        )

        print(
            f"GitHub repositories found: "
            f"{github_count}"
        )

        print(
            "============================="
        )

if __name__ == "__main__":

    asyncio.run(main())