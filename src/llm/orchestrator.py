import asyncio
import json
import os
import sys

import aiohttp
from dotenv import load_dotenv


# ============================================================
# ADD SRC DIRECTORY TO PYTHON PATH
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

from llm.chunker import chunk_text
from llm.providers import (
    call_groq,
    LLMError
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# EXTRACTION PROMPT
# ============================================================

EXTRACTION_PROMPT = """
You are a research-paper information extraction system.

Extract ONLY information explicitly supported by
the supplied text.

DO NOT invent, guess, or infer facts.

Return ONLY valid JSON.

Use exactly this structure:

{
  "problem": "",
  "methods": [],
  "datasets": [],
  "metrics": [],
  "key_findings": [],
  "limitations": []
}

Rules:

1. "problem":
   Describe the research problem only if explicitly
   stated or clearly described in the supplied text.

2. "methods":
   List methods, models, frameworks, algorithms,
   techniques, or approaches explicitly mentioned.

3. "datasets":
   List datasets or benchmarks explicitly mentioned.

4. "metrics":
   List evaluation metrics or scores explicitly mentioned.

5. "key_findings":
   List important results or findings explicitly supported
   by the text.

6. "limitations":
   List limitations only when explicitly mentioned.
   DO NOT invent limitations.

If information is not available, use:
- empty string for "problem"
- empty list for all other fields

Return ONLY JSON.
Do not use Markdown code fences.

TEXT:
"""


# ============================================================
# JSON RESPONSE PARSER
# ============================================================

def parse_json_response(response):
    """
    Convert the LLM response into a Python dictionary.
    """

    if not response:
        raise ValueError(
            "LLM returned an empty response"
        )

    response = response.strip()

    # Remove Markdown code fences if the model
    # accidentally returns them.
    if response.startswith("```"):

        lines = response.splitlines()

        lines = [
            line
            for line in lines
            if not line.strip().startswith("```")
        ]

        response = "\n".join(lines).strip()

    try:

        data = json.loads(response)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Invalid JSON returned by Groq: {error}\n"
            f"Raw response:\n{response}"
        )

    return data


# ============================================================
# VALIDATE EXTRACTION STRUCTURE
# ============================================================

def validate_extraction(data):
    """
    Make sure the LLM returned the required structure.
    """

    required_fields = {
        "problem": str,
        "methods": list,
        "datasets": list,
        "metrics": list,
        "key_findings": list,
        "limitations": list
    }

    if not isinstance(data, dict):
        raise ValueError(
            "LLM response is not a JSON object"
        )

    for field, expected_type in required_fields.items():

        if field not in data:
            raise ValueError(
                f"Missing required field: {field}"
            )

        if not isinstance(
            data[field],
            expected_type
        ):
            raise ValueError(
                f"Invalid type for field '{field}'. "
                f"Expected {expected_type.__name__}"
            )

    return True


# ============================================================
# GROQ LLM CALL
# ============================================================

async def call_with_fallback(
    session,
    prompt
):
    """
    Groq-only LLM extraction.

    Groq is currently the working provider for this project.
    """

    print(
        "Using LLM provider: Groq"
    )

    try:

        response = await call_groq(
            session,
            prompt
        )

        parsed = parse_json_response(
            response
        )

        validate_extraction(
            parsed
        )

        return {
            "provider": "groq",
            "data": parsed
        }

    except Exception as error:

        raise LLMError(
            f"Groq extraction failed: {error}"
        )


# ============================================================
# EXTRACT PAPER INFORMATION
# ============================================================

async def extract_paper(
    session,
    paper
):
    """
    Extract structured information from a research paper.

    Currently uses the paper abstract.
    Long text is divided into chunks.
    """

    content = paper.get(
        "content",
        {}
    )

    abstract = content.get(
        "abstract",
        ""
    )

    # --------------------------------------------------------
    # No abstract
    # --------------------------------------------------------

    if not abstract:

        return {
            "provider": "none",
            "problem": "",
            "methods": [],
            "datasets": [],
            "metrics": [],
            "key_findings": [],
            "limitations": []
        }

    # --------------------------------------------------------
    # Split long abstract/text into chunks
    # --------------------------------------------------------

    chunks = chunk_text(
        abstract,
        max_chars=12000,
        overlap=500
    )

    print(
        f"Text chunks: {len(chunks)}"
    )

    results = []

    # --------------------------------------------------------
    # Process each chunk
    # --------------------------------------------------------

    for chunk_number, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"Processing chunk "
            f"{chunk_number}/{len(chunks)}"
        )

        prompt = (
            EXTRACTION_PROMPT
            + "\n"
            + chunk
        )

        result = await call_with_fallback(
            session,
            prompt
        )

        results.append(
            result
        )

    # --------------------------------------------------------
    # If only one chunk
    # --------------------------------------------------------

    if len(results) == 1:

        return {
            "provider": results[0]["provider"],
            **results[0]["data"]
        }

    # --------------------------------------------------------
    # Combine multiple chunks
    # --------------------------------------------------------

    combined = {
        "provider": "groq",
        "problem": "",
        "methods": [],
        "datasets": [],
        "metrics": [],
        "key_findings": [],
        "limitations": []
    }

    for result in results:

        data = result["data"]

        # Problem
        if (
            not combined["problem"]
            and data.get("problem")
        ):

            combined["problem"] = (
                data["problem"]
            )

        # List fields
        for field in [
            "methods",
            "datasets",
            "metrics",
            "key_findings",
            "limitations"
        ]:

            values = data.get(
                field,
                []
            )

            if isinstance(
                values,
                list
            ):

                combined[field].extend(
                    values
                )

    # --------------------------------------------------------
    # Remove duplicate values
    # --------------------------------------------------------

    for field in [
        "methods",
        "datasets",
        "metrics",
        "key_findings",
        "limitations"
    ]:

        # Preserve order while removing duplicates
        combined[field] = list(
            dict.fromkeys(
                combined[field]
            )
        )

    return combined


# ============================================================
# TEST ONE PAPER
# ============================================================

async def main():

    input_file = (
        "data/processed/"
        "huggingface_enriched_papers.json"
    )

    # --------------------------------------------------------
    # Check input file
    # --------------------------------------------------------

    if not os.path.exists(
        input_file
    ):

        print(
            f"ERROR: File not found:\n"
            f"{input_file}"
        )

        return

    # --------------------------------------------------------
    # Load papers
    # --------------------------------------------------------

    with open(
        input_file,
        "r",
        encoding="utf-8"
    ) as file:

        papers = json.load(
            file
        )

    if not papers:

        print(
            "ERROR: No papers found."
        )

        return

    # --------------------------------------------------------
    # Test first paper only
    # --------------------------------------------------------

    paper = papers[0]

    title = paper.get(
        "content",
        {}
    ).get(
        "title",
        "Unknown title"
    )

    print(
        "\n========== TEST PAPER =========="
    )

    print(
        title
    )

    print(
        "\n========== LLM EXTRACTION =========="
    )

    # --------------------------------------------------------
    # Create HTTP session
    # --------------------------------------------------------

    connector = aiohttp.TCPConnector(
        limit=2
    )

    async with aiohttp.ClientSession(
        connector=connector
    ) as session:

        try:

            result = await extract_paper(
                session,
                paper
            )

            print(
                "\n========== LLM RESULT =========="
            )

            print(
                json.dumps(
                    result,
                    indent=4,
                    ensure_ascii=False
                )
            )

        except Exception as error:

            print(
                "\n========== LLM ERROR =========="
            )

            print(
                error
            )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )