import gc
from functools import wraps


def collect_garbage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        gc.collect()
        return result

    return wrapper
