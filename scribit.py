__doc__ == """logging decoroator
"""
from datetime import datetime
console_log_level = 0




def log(message, category='INFO', level=0):

    if level >= console_log_level:
        print "[%s][%s] %s" % (category, datetime.now(), message)

def log_error(message):
    log(message, category= "ERR")

def logged(a_func, category='INFO', level=0):

    def logged_call(*args, **kw):
        a_func.__doc__
        if not a_func.__doc__:
            log('%s(%s, %s)' % (a_func.__name__, args, kw))
        else:
            log(a_func.__doc__, category, level)
        result = a_func(*args, **kw)
        return result

    logged_call.__name__ = a_func.__name__
    logged_call.__doc__ = a_func.__doc__ 

    return logged_call


def timed(a_func):
    def timed_call(*args, **kw):
        a_func.__doc__
        start = datetime.now()
        result = a_func(*args, **kw)
        stop = datetime.now()
        delta = (stop-start)
        delta_t = delta.seconds + (delta.microseconds / 1000000.0)
        log ('%s took %0.3f' % (a_func.__name__, delta_t), 'PERF')
        return result

    timed_call.__name__ = a_func.__name__
    timed_call.__doc__ = a_func.__doc__
    return timed_call

