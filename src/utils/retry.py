import asyncio
import random


async def retry_async(
    func,
    retries=6,
    base_delay=30,
    max_delay=300
):
    """
    Retry async API calls using exponential backoff.

    Especially useful for API rate limits.
    """

    last_error = None

    for attempt in range(retries):

        try:
            return await func()

        except Exception as error:

            last_error = error

            error_text = str(error).lower()

            # ==================================================
            # RATE LIMIT
            # ==================================================

            if (
                "429" in error_text
                or "rate limit" in error_text
                or "too many requests" in error_text
            ):

                delay = min(
                    base_delay * (2 ** attempt),
                    max_delay
                )

                delay += random.uniform(
                    0,
                    5
                )

                print(
                    "\nRate limit detected."
                )

                print(
                    f"Waiting {delay:.2f} seconds "
                    f"before retry "
                    f"{attempt + 1}/{retries}..."
                )

                await asyncio.sleep(
                    delay
                )

                continue

            # ==================================================
            # OTHER ERRORS
            # ==================================================

            delay = min(
                base_delay * (2 ** attempt),
                max_delay
            )

            delay += random.uniform(
                0,
                5
            )

            print(
                f"Retrying after "
                f"{delay:.2f}s..."
            )

            await asyncio.sleep(
                delay
            )

    raise last_error