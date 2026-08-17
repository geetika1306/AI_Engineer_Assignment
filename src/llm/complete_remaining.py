import json
import os


INPUT_FILE = (
    "data/processed/"
    "huggingface_enriched_papers.json"
)

LLM_FILE = (
    "data/processed/"
    "llm_extracted_papers.json"
)

OUTPUT_FILE = (
    "data/processed/"
    "final_papers.json"
)


EMPTY_EXTRACTION = {
    "provider": "not_available",
    "problem": "",
    "methods": [],
    "datasets": [],
    "metrics": [],
    "key_findings": [],
    "limitations": []
}


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    print(
        "\n========================================"
    )
    print(
        "FINAL DATASET CONSTRUCTION"
    )
    print(
        "========================================"
    )

    # --------------------------------------------------------
    # Load all 1000 papers
    # --------------------------------------------------------

    papers = load_json(
        INPUT_FILE
    )

    print(
        f"Input papers: {len(papers)}"
    )

    # --------------------------------------------------------
    # Load existing LLM results
    # --------------------------------------------------------

    if os.path.exists(LLM_FILE):

        llm_results = load_json(
            LLM_FILE
        )

    else:

        llm_results = []

    print(
        f"LLM results available: "
        f"{len(llm_results)}"
    )

    # --------------------------------------------------------
    # IMPORTANT
    #
    # LLM results were processed sequentially.
    #
    # Therefore:
    #
    # llm_results[0] -> papers[0]
    # llm_results[1] -> papers[1]
    # ...
    #
    # --------------------------------------------------------

    final_papers = []

    llm_count = 0
    fallback_count = 0

    for index, paper in enumerate(
        papers
    ):

        result = dict(
            paper
        )

        # ----------------------------------------------------
        # Use LLM result if available
        # ----------------------------------------------------

        if index < len(llm_results):

            llm_paper = llm_results[index]

            extraction = (
                llm_paper.get(
                    "llm_extraction"
                )
            )

            status = (
                llm_paper.get(
                    "llm_extraction_status"
                )
            )

            if (
                extraction
                and status == "success"
            ):

                result[
                    "llm_extraction"
                ] = extraction

                result[
                    "llm_extraction_status"
                ] = "success"

                llm_count += 1

            else:

                result[
                    "llm_extraction"
                ] = dict(
                    EMPTY_EXTRACTION
                )

                result[
                    "llm_extraction_status"
                ] = "not_processed"

                fallback_count += 1

        # ----------------------------------------------------
        # No LLM result exists
        # ----------------------------------------------------

        else:

            result[
                "llm_extraction"
            ] = dict(
                EMPTY_EXTRACTION
            )

            result[
                "llm_extraction_status"
            ] = "not_processed"

            fallback_count += 1

        final_papers.append(
            result
        )

    # --------------------------------------------------------
    # Save final dataset
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            final_papers,
            file,
            indent=4,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "FINAL DATASET READY"
    )

    print(
        "========================================"
    )

    print(
        f"Total papers: "
        f"{len(final_papers)}"
    )

    print(
        f"LLM extracted: "
        f"{llm_count}"
    )

    print(
        f"Not LLM processed: "
        f"{fallback_count}"
    )

    print(
        "\nSaved to:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":

    main()