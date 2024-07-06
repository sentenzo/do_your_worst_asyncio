import asyncio
from functools import wraps
from time import time


def timeit(f):
    if asyncio.iscoroutinefunction(f):

        @wraps(f)
        async def wrap(*args, **kw):
            ts = time()
            result = await f(*args, **kw)
            te = time()
            print(
                "coro:%r args:[%r, %r] took: %2.4f sec"
                % (f.__name__, args, kw, te - ts)
            )
            return result

        return wrap

    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(
            "func:%r args:[%r, %r] took: %2.4f sec"
            % (f.__name__, args, kw, te - ts)
        )
        return result

    return wrap
