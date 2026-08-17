import json
import os


FINAL_FILE = "data/processed/final_papers.json"


def test_final_file_exists():
    assert os.path.exists(FINAL_FILE)


def test_final_dataset_has_1000_papers():

    with open(
        FINAL_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        papers = json.load(file)

    assert len(papers) == 1000


def test_required_fields_exist():

    with open(
        FINAL_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        papers = json.load(file)

    required_fields = [
        "schemaVersion",
        "recordType",
        "source",
        "content",
        "collectedAt",
        "llm_extraction",
        "llm_extraction_status"
    ]

    for paper in papers:

        for field in required_fields:

            assert field in paper


def test_content_fields_exist():

    with open(
        FINAL_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        papers = json.load(file)

    for paper in papers:

        content = paper["content"]

        assert "title" in content
        assert "authors" in content
        assert "abstract" in content


def test_llm_extraction_structure():

    with open(
        FINAL_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        papers = json.load(file)

    expected_fields = [
        "problem",
        "methods",
        "datasets",
        "metrics",
        "key_findings",
        "limitations"
    ]

    for paper in papers:

        extraction = paper[
            "llm_extraction"
        ]

        for field in expected_fields:

            assert field in extraction


def test_llm_success_count():

    with open(
        FINAL_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        papers = json.load(file)

    successful = sum(
        1
        for paper in papers
        if paper[
            "llm_extraction_status"
        ] == "success"
    )

    assert successful == 230