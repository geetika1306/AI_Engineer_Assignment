import asyncio
import aiohttp

from utils.paper_metadata import (
    get_verified_github_info
)


async def main():

    async with aiohttp.ClientSession() as session:

        result = await get_verified_github_info(
            session,
            "2608.13560"
        )

        print(result)


if __name__ == "__main__":
    asyncio.run(main()) 