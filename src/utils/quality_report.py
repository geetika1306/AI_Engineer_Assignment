import json
import os
from collections import Counter


INPUT_FILE = "data/processed/resolved_papers.json"
OUTPUT_FILE = "data/processed/quality_report.json"


def load_data():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def generate_report(papers):

    total = len(papers)

    github_matches = sum(
        1
        for paper in papers
        if paper["content"].get(
            "github_url"
        )
    )

    github_stars_available = sum(
        1
        for paper in papers
        if paper["content"].get(
            "github_stars"
        ) is not None
    )

    confidence_counts = Counter(
        paper["content"].get(
            "match_confidence",
            0.0
        )
        for paper in papers
    )

    source_counts = Counter(
        paper.get(
            "source",
            {}
        ).get(
            "name",
            "unknown"
        )
        for paper in papers
    )

    missing_titles = sum(
        1
        for paper in papers
        if not paper["content"].get(
            "title"
        )
    )

    missing_authors = sum(
        1
        for paper in papers
        if not paper["content"].get(
            "authors"
        )
    )

    missing_abstracts = sum(
        1
        for paper in papers
        if not paper["content"].get(
            "abstract"
        )
    )

    report = {

        "total_records": total,

        "github": {
            "matched": github_matches,
            "unmatched": (
                total - github_matches
            ),
            "stars_available": (
                github_stars_available
            )
        },

        "confidence_distribution": {
            str(key): value
            for key, value
            in confidence_counts.items()
        },

        "sources": dict(
            source_counts
        ),

        "missing_fields": {
            "title": missing_titles,
            "authors": missing_authors,
            "abstract": missing_abstracts
        }
    }

    return report


def main():

    papers = load_data()

    report = generate_report(
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
            report,
            file,
            indent=4
        )

    print(
        "\n========== QUALITY REPORT =========="
    )

    print(
        f"Total records: "
        f"{report['total_records']}"
    )

    print(
        f"GitHub matches: "
        f"{report['github']['matched']}"
    )

    print(
        f"GitHub unmatched: "
        f"{report['github']['unmatched']}"
    )

    print(
        f"GitHub stars available: "
        f"{report['github']['stars_available']}"
    )

    print(
        "\nMissing fields:"
    )

    for field, count in report[
        "missing_fields"
    ].items():

        print(
            f"  {field}: {count}"
        )

    print(
        "\nSaved to:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()