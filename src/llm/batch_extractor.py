import asyncio
import json
import os
import sys


# ============================================================
# PYTHON PATH
# ============================================================

SRC_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# ============================================================
# IMPORTS
# ============================================================

import aiohttp

from llm.orchestrator import extract_paper


# ============================================================
# FILE PATHS
# ============================================================

INPUT_FILE = (
    "data/processed/"
    "huggingface_enriched_papers.json"
)

OUTPUT_FILE = (
    "data/processed/"
    "llm_extracted_papers.json"
)

CHECKPOINT_FILE = (
    "data/processed/"
    "llm_checkpoint.json"
)


# ============================================================
# SETTINGS
# ============================================================

# One paper at a time is safest for Groq.
BATCH_SIZE = 1

# Delay between successful requests.
REQUEST_DELAY = 10
RETRY_DELAY = 60
# ============================================================
# LOAD JSON
# ============================================================

def load_json(path, default):

    if not os.path.exists(path):

        return default

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            f"Could not read {path}: {error}"
        )

        return default


# ============================================================
# SAVE JSON SAFELY
# ============================================================

def save_json(path, data):

    directory = os.path.dirname(path)

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    temp_file = path + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    # Replace the original only after the
    # temporary file has been written successfully.
    os.replace(
        temp_file,
        path
    )


# ============================================================
# PROCESS ONE PAPER
# ============================================================

async def process_paper(
    session,
    paper,
    index
):

    title = (
        paper
        .get("content", {})
        .get(
            "title",
            "Unknown title"
        )
    )

    print(
        f"\nPaper {index + 1}"
    )

    print(
        f"Title: {title}"
    )

    try:

        extraction = await extract_paper(
            session,
            paper
        )

        # Store extraction result.
        paper["llm_extraction"] = extraction

        # Mark successful.
        paper[
            "llm_extraction_status"
        ] = "success"

        # Remove previous error if this paper
        # is being retried successfully.
        paper.pop(
            "llm_extraction_error",
            None
        )

        print(
            "Status: SUCCESS"
        )

        return paper

    except Exception as error:

        # Store failure information.
        paper[
            "llm_extraction_status"
        ] = "failed"

        paper[
            "llm_extraction_error"
        ] = str(error)

        print(
            "Status: FAILED"
        )

        print(
            f"Error: {error}"
        )

        return paper


# ============================================================
# MAIN
# ============================================================

async def main():

    print(
        "\n========================================"
    )

    print(
        "Groq LLM Batch Extraction"
    )

    print(
        "========================================"
    )

    # --------------------------------------------------------
    # LOAD INPUT PAPERS
    # --------------------------------------------------------

    papers = load_json(
        INPUT_FILE,
        []
    )

    if not papers:

        print(
            "ERROR: No papers found."
        )

        return

    total = len(papers)

    print(
        f"Total papers: {total}"
    )

    # --------------------------------------------------------
    # LOAD EXISTING RESULTS
    # --------------------------------------------------------

    results = load_json(
        OUTPUT_FILE,
        []
    )

    print(
        f"Existing results: {len(results)}"
    )

    # --------------------------------------------------------
    # LOAD CHECKPOINT
    # --------------------------------------------------------

    checkpoint = load_json(
        CHECKPOINT_FILE,
        {
            "last_processed": 0,
            "total": total
        }
    )

    checkpoint_index = checkpoint.get(
        "last_processed",
        0
    )

    print(
        f"Checkpoint: {checkpoint_index}"
    )

    # --------------------------------------------------------
    # DETERMINE STARTING POINT
    # --------------------------------------------------------

    start_index = checkpoint_index

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # If the last checkpointed paper failed,
    # retry it instead of skipping it.
    #
    # The old version may have saved 239/1000
    # even though paper 239 failed.
    # --------------------------------------------------------

    if (
        start_index > 0
        and start_index <= len(results)
    ):

        previous_index = (
            start_index - 1
        )

        previous_result = (
            results[previous_index]
        )

        previous_status = (
            previous_result.get(
                "llm_extraction_status"
            )
        )

        if previous_status == "failed":

            print(
                "\nLast checkpointed paper failed."
            )

            print(
                f"Retrying paper "
                f"{start_index}"
            )

            start_index = (
                start_index - 1
            )

    # --------------------------------------------------------
    # SAFETY:
    #
    # Make sure start_index is valid.
    # --------------------------------------------------------

    if start_index < 0:

        start_index = 0

    if start_index > total:

        start_index = total

    print(
        f"Resuming from paper: "
        f"{start_index + 1}"
    )

    # --------------------------------------------------------
    # ALL PAPERS ALREADY PROCESSED
    # --------------------------------------------------------

    if start_index >= total:

        print(
            "\nAll papers are already processed."
        )

        print(
            f"Output file:"
        )

        print(
            OUTPUT_FILE
        )

        return

    # --------------------------------------------------------
    # HTTP SESSION
    # --------------------------------------------------------

    connector = aiohttp.TCPConnector(
        limit=1
    )

    async with aiohttp.ClientSession(
        connector=connector
    ) as session:

        # ----------------------------------------------------
        # PROCESS PAPERS
        # ----------------------------------------------------

        for index in range(
            start_index,
            total
        ):

            paper = papers[index]

            # ------------------------------------------------
            # RETRY LOOP
            #
            # A paper remains here until it succeeds.
            # ------------------------------------------------

            while True:

                result = await process_paper(
                    session,
                    paper,
                    index
                )

                # ============================================
                # SUCCESS
                # ============================================

                if (
                    result.get(
                        "llm_extraction_status"
                    )
                    == "success"
                ):

                    # ----------------------------------------
                    # Store result
                    # ----------------------------------------

                    if index < len(results):

                        results[index] = result

                    else:

                        # Fill any missing positions
                        # if necessary.
                        while len(results) < index:

                            results.append({})

                        results.append(
                            result
                        )

                    # ----------------------------------------
                    # Save output
                    # ----------------------------------------

                    save_json(
                        OUTPUT_FILE,
                        results
                    )

                    # ----------------------------------------
                    # Advance checkpoint ONLY after success
                    # ----------------------------------------

                    save_json(
                        CHECKPOINT_FILE,
                        {
                            "last_processed": index + 1,
                            "total": total
                        }
                    )

                    print(
                        f"Checkpoint saved: "
                        f"{index + 1}/{total}"
                    )

                    # ----------------------------------------
                    # Delay before next paper
                    # ----------------------------------------

                    if (
                        index + 1
                        < total
                    ):

                        await asyncio.sleep(
                            REQUEST_DELAY
                        )

                    # ----------------------------------------
                    # Move to next paper
                    # ----------------------------------------

                    break

                # ============================================
                # FAILURE
                # ============================================

                else:

                    # ----------------------------------------
                    # Save failed result WITHOUT advancing
                    # checkpoint.
                    # ----------------------------------------

                    if index < len(results):

                        results[index] = result

                    else:

                        while len(results) < index:

                            results.append({})

                        results.append(
                            result
                        )

                    save_json(
                        OUTPUT_FILE,
                        results
                    )

                    print(
                        f"\nPaper {index + 1} failed."
                    )

                    print(
                        "Checkpoint NOT advanced."
                    )

                    print(
                        f"Waiting "
                        f"{RETRY_DELAY} seconds "
                        f"before retry..."
                    )

                    # ----------------------------------------
                    # Wait before retry
                    # ----------------------------------------

                    await asyncio.sleep(
                        RETRY_DELAY
                    )

                    # ----------------------------------------
                    # Retry SAME paper
                    # ----------------------------------------

                    continue

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    successful = sum(
        1
        for paper in results
        if paper.get(
            "llm_extraction_status"
        ) == "success"
    )

    failed = sum(
        1
        for paper in results
        if paper.get(
            "llm_extraction_status"
        ) == "failed"
    )

    print(
        "\n========================================"
    )

    print(
        "LLM EXTRACTION SUMMARY"
    )

    print(
        "========================================"
    )

    print(
        f"Total papers: {total}"
    )

    print(
        f"Successful: {successful}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        "\nOutput file:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nCheckpoint file:"
    )

    print(
        CHECKPOINT_FILE
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )