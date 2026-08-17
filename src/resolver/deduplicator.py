import json
import os
import re
import hashlib


INPUT_FILE = "data/processed/normalized_papers.json"
OUTPUT_FILE = "data/processed/deduplicated_papers.json"


def normalize_title(title):
    """
    Normalize a title so small formatting differences
    don't create duplicate records.
    """

    if not title:
        return ""

    title = title.lower()

    # Remove punctuation
    title = re.sub(
        r"[^a-z0-9\s]",
        "",
        title
    )

    # Normalize whitespace
    title = re.sub(
        r"\s+",
        " ",
        title
    ).strip()

    return title


def create_paper_key(paper):
    """
    Create a stable identifier for a paper.

    Prefer arXiv ID because it is a strong
    source-specific identifier.
    """

    content = paper.get(
        "content",
        {}
    )

    arxiv_id = content.get(
        "arxiv_id"
    )

    if arxiv_id:
        return f"arxiv:{arxiv_id}"

    paper_url = content.get(
        "paper_url"
    )

    if paper_url:
        return f"url:{paper_url.lower().strip()}"

    title = normalize_title(
        content.get(
            "title",
            ""
        )
    )

    authors = content.get(
        "authors",
        []
    )

    author_string = "|".join(
        sorted(
            author.lower().strip()
            for author in authors
        )
    )

    raw_key = (
        f"{title}|{author_string}"
    )

    return "hash:" + hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()


def deduplicate_papers(papers):

    unique = {}
    duplicates = 0

    for paper in papers:

        key = create_paper_key(
            paper
        )

        if key in unique:

            duplicates += 1

            continue

        unique[key] = paper

    return list(
        unique.values()
    ), duplicates


def main():

    print(
        "Loading normalized papers..."
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

    unique_papers, duplicates = (
        deduplicate_papers(
            papers
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
            unique_papers,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"\nUnique papers: "
        f"{len(unique_papers)}"
    )

    print(
        f"Duplicates removed: "
        f"{duplicates}"
    )

    print(
        f"\nSaved to:\n"
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()