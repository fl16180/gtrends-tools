from __future__ import absolute_import, print_function
from functools import wraps
import time


def retry(count=3, delay=2):
    ''' retries function when exception is raised.

        count: number of retries before failure
        delay: time to wait in seconds before retry
    '''
    def decorator(func):
        @wraps(func)
        def result(*args, **kwargs):
            for _ in range(count):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(e)
                    print('Retrying after {0} s'.format(delay))
                    time.sleep(delay)
        return result
    return decorator


def timeit(func):
    ''' decorator for timing a function
    '''
    @wraps(func)
    def wrap(*args, **kw):
        ts = time.time()
        result = func(*args, **kw)
        te = time.time()
        print('Time elapsed: {0} s'.format(te - ts))
        return result
    return wrap
