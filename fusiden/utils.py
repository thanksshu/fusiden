'''
used functions
'''
import random
import time


def pack(func, *, args=None, kwargs=None, delay=0, random_ratio=0.1):
    """
    pack up function with argument
    
    delay -- delay before action
    """
    if args is None:
        args = list()
    if kwargs is None:
        kwargs = dict()

    def wrapper(*, task_info=None):
        rsleep(delay, random_ratio)
        print(f'{func.__name__} {args} {kwargs}')
        return func(task_info=task_info, *args, **kwargs)
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


def rsleep(timeout, random_ratio=0.2, *, task_info=None):
    """
    random sleep time
    """
    time.sleep(timeout + random.uniform(0, timeout * random_ratio))


def tprint(args='', *, print_kwargs=dict(), task_info=None):
    '''
    用于任务的打印
    '''
    print(args, **print_kwargs)


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
