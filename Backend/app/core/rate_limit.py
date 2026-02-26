import time
from collections import defaultdict

from fastapi import HTTPException, Request, status


class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _cleanup(self, key: str) -> None:
        now = time.monotonic()
        self._requests[key] = [
            t for t in self._requests[key] if now - t < self.window_seconds
        ]
        if not self._requests[key]:
            del self._requests[key]

    def check(self, key: str) -> None:
        self._cleanup(key)
        if len(self._requests.get(key, [])) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Quá nhiều yêu cầu. Vui lòng thử lại sau.",
            )
        self._requests[key].append(time.monotonic())


auth_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)


async def check_auth_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    auth_rate_limiter.check(client_ip)
