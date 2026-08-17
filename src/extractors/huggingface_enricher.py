import asyncio
import json
import os
import sys

import aiohttp


# Add src directory to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)


from utils.retry import retry_async


INPUT_FILE = "data/processed/resolved_papers.json"
OUTPUT_FILE = "data/processed/huggingface_enriched_papers.json"

HF_PAPER_API = "https://huggingface.co/api/papers"


async def fetch_hf_paper(
    session,
    arxiv_id
):
    """
    Fetch paper metadata from Hugging Face.
    """

    url = f"{HF_PAPER_API}/{arxiv_id}"

    async def request():

        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(
                total=20
            )
        ) as response:

            if response.status == 404:
                return None

            response.raise_for_status()

            return await response.json()

    try:

        return await retry_async(
            request,
            retries=3,
            base_delay=1
        )

    except Exception as error:

        print(
            f"HF lookup failed for "
            f"{arxiv_id}: {error}"
        )

        return None


async def enrich_paper(
    session,
    paper,
    semaphore
):

    async with semaphore:

        content = paper.get(
            "content",
            {}
        )

        arxiv_id = content.get(
            "arxiv_id"
        )

        if not arxiv_id:
            return paper

        # Don't overwrite an existing
        # verified GitHub match.
        if content.get("github_url"):
            return paper

        metadata = await fetch_hf_paper(
            session,
            arxiv_id
        )

        if not metadata:
            return paper

        github_url = metadata.get(
            "githubRepo"
        )

        if github_url:

            content["github_url"] = (
                github_url
            )

            content[
                "github_stars"
            ] = metadata.get(
                "githubStars"
            )

            content[
                "match_confidence"
            ] = 1.0

            content[
                "match_method"
            ] = "huggingface_paper_metadata"

            content[
                "match_explanation"
            ] = (
                "GitHub repository was explicitly "
                "associated with the paper by the "
                "Hugging Face Papers metadata."
            )

        # Save additional Hugging Face metadata.

        if metadata.get("projectPage"):

            content[
                "project_page"
            ] = metadata.get(
                "projectPage"
            )

        if metadata.get("ai_keywords"):

            content[
                "keywords"
            ] = metadata.get(
                "ai_keywords"
            )

        if metadata.get("linkedModels"):

            content[
                "linked_models"
            ] = metadata.get(
                "linkedModels"
            )

        if metadata.get("linkedDatasets"):

            content[
                "linked_datasets"
            ] = metadata.get(
                "linkedDatasets"
            )

        return paper


async def enrich_all(
    papers
):

    # Maximum 5 simultaneous HF requests.
    semaphore = asyncio.Semaphore(5)

    connector = aiohttp.TCPConnector(
        limit=10
    )

    async with aiohttp.ClientSession(
        connector=connector
    ) as session:

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


def main():

    print(
        "Loading resolved papers..."
    )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        papers = json.load(file)

    print(
        f"Input papers: {len(papers)}"
    )

    enriched = asyncio.run(
        enrich_all(papers)
    )

    github_matches = sum(
        1
        for paper in enriched
        if paper["content"].get(
            "github_url"
        )
    )

    os.makedirs(
        os.path.dirname(
            OUTPUT_FILE
        ),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            enriched,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "\n========== HUGGING FACE =========="
    )

    print(
        f"Total papers: {len(enriched)}"
    )

    print(
        f"GitHub matches after enrichment: "
        f"{github_matches}"
    )

    print(
        "\nSaved to:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()