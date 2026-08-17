import asyncio
import time


class RateLimiter:

    def __init__(self, rate_per_second):
        self.rate = rate_per_second
        self.interval = 1 / rate_per_second
        self.lock = asyncio.Lock()
        self.last_request = 0

    async def wait(self):

        async with self.lock:

            now = time.monotonic()

            elapsed = (
                now - self.last_request
            )

            if elapsed < self.interval:

                await asyncio.sleep(
                    self.interval - elapsed
                )

            self.last_request = (
                time.monotonic()
            )