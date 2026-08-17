import json
import os
from urllib.parse import urlparse


INPUT_FILE = "data/processed/deduplicated_papers.json"
OUTPUT_FILE = "data/processed/resolved_papers.json"


def normalize_github_url(url):
    """
    Normalize a GitHub repository URL.
    """

    if not url:
        return None

    url = url.strip().rstrip("/")

    if url.endswith(".git"):
        url = url[:-4]

    return url


def resolve_github(paper):
    """
    Resolve a paper to a GitHub repository.

    Since the GitHub URL comes from verified paper
    metadata, this receives a high confidence score.
    """

    content = paper.get(
        "content",
        {}
    )

    github_url = normalize_github_url(
        content.get("github_url")
    )

    if not github_url:
        return {
            "github_url": None,
            "github_stars": None,
            "match_confidence": 0.0,
            "match_method": None,
            "match_explanation": (
                "No verified GitHub repository "
                "was found for this paper."
            )
        }

    parsed = urlparse(
        github_url
    )

    # Verify that the URL actually points
    # to GitHub.
    if parsed.netloc.lower() not in (
        "github.com",
        "www.github.com"
    ):
        return {
            "github_url": None,
            "github_stars": None,
            "match_confidence": 0.0,
            "match_method": None,
            "match_explanation": (
                "Repository URL is not a GitHub URL."
            )
        }

    return {
        "github_url": github_url,

        "github_stars": content.get(
            "github_stars"
        ),

        "match_confidence": 1.0,

        "match_method": (
            "verified_paper_metadata"
        ),

        "match_explanation": (
            "GitHub repository was explicitly "
            "associated with the paper by the "
            "paper metadata provider."
        )
    }


def resolve_papers(papers):

    resolved = []

    for paper in papers:

        resolution = resolve_github(
            paper
        )

        paper["content"][
            "github_url"
        ] = resolution[
            "github_url"
        ]

        paper["content"][
            "github_stars"
        ] = resolution[
            "github_stars"
        ]

        paper["content"][
            "match_confidence"
        ] = resolution[
            "match_confidence"
        ]

        paper["content"][
            "match_method"
        ] = resolution[
            "match_method"
        ]

        paper["content"][
            "match_explanation"
        ] = resolution[
            "match_explanation"
        ]

        resolved.append(
            paper
        )

    return resolved


def main():

    print(
        "Loading deduplicated papers..."
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

    resolved_papers = resolve_papers(
        papers
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
            resolved_papers,
            file,
            indent=4,
            ensure_ascii=False
        )

    matched = sum(
        1
        for paper in resolved_papers
        if paper["content"].get(
            "github_url"
        )
    )

    print(
        f"\nResolved papers: "
        f"{len(resolved_papers)}"
    )

    print(
        f"GitHub matches: {matched}"
    )

    print(
        f"GitHub unmatched: "
        f"{len(resolved_papers) - matched}"
    )

    print(
        f"\nSaved to:\n"
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()