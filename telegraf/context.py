"""
Decorator for async methods.

Requires Python 3.5 or higher.
"""
# stdlib
from functools import wraps
from time import time


def wrapped_coroutine(self, func):
    """Timing wrapper for async functions."""
    @wraps(func)
    async def wrapped_co(*args, **kwargs):  # noqa
        start = time()
        try:
            return await func(*args, **kwargs)
        finally:
            self._send(start)
    return wrapped_co
