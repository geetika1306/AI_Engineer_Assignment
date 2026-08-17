import json
import os
from datetime import datetime, timezone


INPUT_FILE = (
    "data/processed/"
    "huggingface_enriched_papers.json"
)

OUTPUT_FILE = (
    "data/output/"
    "final_dataset.json"
)


def build_record(paper):

    content = paper.get(
        "content",
        {}
    )

    source = paper.get(
        "source",
        {}
    )

    github_url = content.get(
        "github_url"
    )

    github_stars = content.get(
        "github_stars"
    )

    confidence = content.get(
        "match_confidence",
        0.0
    )

    match_method = content.get(
        "match_method"
    )

    match_explanation = content.get(
        "match_explanation"
    )

    return {

        "schemaVersion": "1.0",

        "recordType": "RESEARCH_PAPER",

        "source": {
            "name": source.get(
                "name",
                "arXiv"
            ),
            "url": source.get(
                "url"
            )
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
                "abstract",
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

            "github_url": github_url,

            "github_stars": github_stars,

            "project_page": content.get(
                "project_page"
            ),

            "keywords": content.get(
                "keywords",
                []
            ),

            "linked_models": content.get(
                "linked_models",
                []
            ),

            "linked_datasets": content.get(
                "linked_datasets",
                []
            )
        },

        "resolution": {

            "matched": (
                github_url is not None
            ),

            "confidence": confidence,

            "method": match_method,

            "explanation": match_explanation
        },

        "provenance": {

            "collectedAt": paper.get(
                "collectedAt",
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),

            "sources": [
                source.get(
                    "name",
                    "arXiv"
                )
            ]
        }
    }


def main():

    print(
        "Loading enriched papers..."
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

    final_records = []

    for paper in papers:

        record = build_record(
            paper
        )

        final_records.append(
            record
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
            final_records,
            file,
            indent=4,
            ensure_ascii=False
        )

    matched = sum(
        1
        for record in final_records
        if record[
            "resolution"
        ][
            "matched"
        ]
    )

    print(
        "\n========== FINAL DATASET =========="
    )

    print(
        f"Total records: "
        f"{len(final_records)}"
    )

    print(
        f"GitHub matched: {matched}"
    )

    print(
        f"GitHub unmatched: "
        f"{len(final_records) - matched}"
    )

    print(
        "\nSaved to:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()