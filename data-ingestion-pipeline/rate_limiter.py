import time


class RateLimiter:
    def __init__(self, min_interval_seconds: float):
        self._min_interval = min_interval_seconds
        self._last_request_time: float = 0.0

    def wait(self) -> None:
        elapsed = time.time() - self._last_request_time
        wait_time = self._min_interval - elapsed
        if wait_time > 0:
            time.sleep(wait_time)
        self._last_request_time = time.time()
