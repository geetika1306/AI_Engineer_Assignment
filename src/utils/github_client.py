import asyncio
import os
import aiohttp
from dotenv import load_dotenv
from utils.rate_limiter import RateLimiter
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError(
        "GITHUB_TOKEN not found in .env"
    )

github_limiter = RateLimiter(
    rate_per_second=2
)
async def get_github_stars(
    session,
    github_url
):
    """
    Get the current GitHub star count
    asynchronously.
    """

    if not github_url:
        return None

    parts = github_url.rstrip("/").split("/")

    if len(parts) < 2:
        return None

    owner = parts[-2]
    repo = parts[-1]

    # Remove possible .git suffix
    repo = repo.removesuffix(".git")

    api_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}"
    )

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    try:
        await github_limiter.wait()
        async with session.get(
            api_url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(
                total=15
            )
        ) as response:

            if response.status == 404:
                print(
                    f"GitHub repository not found: "
                    f"{github_url}"
                )
                return None

            if response.status == 403:
                print(
                    "GitHub API rate limit or "
                    "permission issue."
                )
                return None

            response.raise_for_status()

            data = await response.json()

            return data.get(
                "stargazers_count"
            )

    except (
        aiohttp.ClientError,
        asyncio.TimeoutError
    ):
        return None