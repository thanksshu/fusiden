'''
used functions
'''


def kill_subproc(popen):
    """
    kill a subproc
    """
    while popen.poll() is None:
        popen.kill()
        popen.wait()


def log_func(func):
    """
    log 装饰器
    """
    def wrapper(*args, **kwargs):
        print(func.__name__)
        return func(*args, **kwargs)
    return wrapper
