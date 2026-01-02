import threading
import queue
import time

_JOB_QUEUE = queue.Queue()


def worker():
    while True:
        func, args = _JOB_QUEUE.get()
        try:
            func(*args)
        except Exception:
            pass
        _JOB_QUEUE.task_done()


_THREAD = threading.Thread(target=worker, daemon=True)
_THREAD.start()


def enqueue(func, *args):
    _JOB_QUEUE.put((func, args))
