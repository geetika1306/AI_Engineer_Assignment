import os
import json
from datetime import datetime, timezone


INPUT_FILE = "data/raw/research_papers.json"
OUTPUT_FILE = "data/processed/normalized_papers.json"


def normalize_paper(paper):
    """
    Convert a raw research-paper record into
    the common assignment schema.
    """

    content = paper.get("content", {})
    source = paper.get("source", {})

    normalized = {
        "schemaVersion": "1.0",
        "recordType": "RESEARCH_PAPER",

        "source": {
            "name": source.get(
                "name",
                "arXiv"
            ),
            "url": source.get("url")
        },

        "content": {
            "title": content.get(
                "title",
                ""
            ),

            "authors": content.get(
                "authors",
                []
            ),

            "abstract": content.get(
                "summary",
                ""
            ),

            "published_date": content.get(
                "published_date"
            ),

            "paper_url": content.get(
                "paper_url"
            ),

            "arxiv_id": content.get(
                "arxiv_id"
            ),

            "github_url": content.get(
                "github_url"
            ),

            "github_stars": content.get(
                "github_stars"
            )
        },

        "collectedAt": paper.get(
            "collectedAt",
            datetime.now(
                timezone.utc
            ).isoformat()
        )
    }

    return normalized


def load_raw_papers():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_normalized_papers(
    papers
):

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
            papers,
            file,
            indent=4,
            ensure_ascii=False
        )


def main():

    print(
        "Loading raw research papers..."
    )

    raw_papers = load_raw_papers()

    print(
        f"Raw papers: {len(raw_papers)}"
    )

    normalized_papers = []

    for paper in raw_papers:

        normalized = normalize_paper(
            paper
        )

        normalized_papers.append(
            normalized
        )

    save_normalized_papers(
        normalized_papers
    )

    print(
        f"\nNormalized papers: "
        f"{len(normalized_papers)}"
    )

    print(
        f"Saved to:\n"
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()