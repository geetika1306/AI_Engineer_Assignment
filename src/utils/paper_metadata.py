import asyncio
import aiohttp

from utils.github_client import get_github_stars
from utils.retry import retry_async


HF_PAPER_API = "https://huggingface.co/api/papers"


async def get_paper_metadata(
    session,
    arxiv_id
):
    """
    Fetch paper metadata asynchronously.

    If the paper is not available from the
    Hugging Face API, return None.

    Network failures are retried using
    exponential backoff with jitter.
    """

    url = f"{HF_PAPER_API}/{arxiv_id}"

    async def request():

        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(
                total=20
            )
        ) as response:

            # Paper is not indexed by Hugging Face.
            # This is not a retryable error.
            if response.status == 404:
                return None

            response.raise_for_status()

            return await response.json()

    try:

        return await retry_async(
            request,
            retries=3,
            base_delay=1
        )

    except (
        aiohttp.ClientError,
        asyncio.TimeoutError
    ):

        return None

    except Exception:

        return None


async def get_verified_github_info(
    session,
    arxiv_id
):
    """
    Find a verified GitHub repository associated
    with an arXiv paper.

    If a repository is found, query GitHub directly
    for its current star count.

    Returns:
        {
            "github_url": str | None,
            "github_stars": int | None
        }
    """

    metadata = await get_paper_metadata(
        session,
        arxiv_id
    )

    # No metadata available
    if not metadata:

        return {
            "github_url": None,
            "github_stars": None
        }

    # Get repository from verified paper metadata
    github_url = metadata.get(
        "githubRepo"
    )

    # No repository associated with paper
    if not github_url:

        return {
            "github_url": None,
            "github_stars": None
        }

    # Get CURRENT GitHub stars directly
    current_stars = await get_github_stars(
        session,
        github_url
    )

    return {
        "github_url": github_url,
        "github_stars": current_stars
    }