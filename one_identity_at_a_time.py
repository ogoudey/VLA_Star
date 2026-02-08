import threading


class SingleIdentityRunningLock:
    def __init__(self, max_waiters=1):
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._active = False
        self._waiting = 0
        self._max_waiters = max_waiters

    def __enter__(self):
        with self._lock:
            # If someone is running
            if self._active:
                # Too many waiters → kill / reject
                if self._waiting >= self._max_waiters:
                    raise RuntimeError("Agent rejected: too many waiting")

                # Otherwise, wait
                self._waiting += 1
                try:
                    while self._active:
                        self._cond.wait()
                finally:
                    self._waiting -= 1

            # Acquire execution
            self._active = True

        return self

    def __exit__(self, exc_type, exc, tb):
        with self._lock:
            self._active = False
            self._cond.notify()  # wake exactly one waiter