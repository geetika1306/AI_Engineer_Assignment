import json
import os


CHECKPOINT_FILE = "data/raw/checkpoint.json"


def save_checkpoint(papers):
    """
    Save the current paper collection so that
    progress is not lost if the scraper stops.
    """

    os.makedirs(
        os.path.dirname(CHECKPOINT_FILE),
        exist_ok=True
    )

    with open(
        CHECKPOINT_FILE,
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
        f"Checkpoint saved: "
        f"{len(papers)} papers"
    )


def load_checkpoint():
    """
    Load previously saved papers.
    """

    if not os.path.exists(
        CHECKPOINT_FILE
    ):
        return []

    try:

        with open(
            CHECKPOINT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            papers = json.load(file)

        print(
            f"Loaded checkpoint: "
            f"{len(papers)} papers"
        )

        return papers

    except (
        json.JSONDecodeError,
        OSError
    ):

        print(
            "Could not load checkpoint."
        )

        return []