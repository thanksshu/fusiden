'''
used functions
'''
import random
import time


def pack(func, *args, **kwargs):
    """
    pack up function with argument
    """
    def wrapper(*, arg=None):
        print(func.__name__, *args, **kwargs)
        return func(arg=arg, *args, **kwargs)
    return wrapper


def kill_subproc(popen):
    """
    kill a subproc
    """
    while popen.poll() is None:
        popen.kill()
        popen.wait()


def log_func(func):
    """
    log decorator
    """
    def wrapper(*args, **kwargs):
        print(func.__name__)
        return func(*args, **kwargs)
    return wrapper


def rsleep(sec, ratio=0.2, *, arg=None):
    """
    random sleep time
    """
    time.sleep(sec + random.uniform(0, sec * ratio))
    return


def gprint(args='', *, kwargs=dict(), arg=None):
    '''
    用于任务的打印
    '''
    print(args, **kwargs)


class Timer():
    """
    timer class
    """

    def __init__(self):
        """
        docstring
        """
        self.start_time = None

    def start(self):
        """
        start timer
        """
        if self.start_time is None:
            self.start_time = time.time()

    def check(self):
        """
        check time passed
        """
        if self.start_time is None:
            return -1
        return time.time() - self.start_time

    def reset(self):
        """
        reset timer
        """
        if self.start_time is not None:
            self.start_time = None
