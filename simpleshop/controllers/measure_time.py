""" Utility functions for measureing time performances
"""
from functools import wraps
from time import time


def measure_time(f):
    """ Measures the executed time on decorated function and prints out data"""
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts))
        return result
    return wrap
