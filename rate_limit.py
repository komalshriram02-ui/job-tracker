import time

from fastapi import HTTPException

MAX_ATTEMPTS = 5
LOCK_SECONDS = 300

_failed = {}


def check_locked(key: str):
    entry = _failed.get(key)
    if not entry:
        return
    count, locked_until = entry
    if locked_until:
        remaining = int(locked_until - time.time())
        if remaining > 0:
            raise HTTPException(
                status_code=429,
                detail=f"Too many failed attempts. Try again in {remaining} seconds.",
            )
        _failed.pop(key, None)


def record_failure(key: str):
    count, _ = _failed.get(key, (0, 0))
    count += 1
    if count >= MAX_ATTEMPTS:
        _failed[key] = (0, time.time() + LOCK_SECONDS)
    else:
        _failed[key] = (count, 0)


def reset(key: str):
    _failed.pop(key, None)