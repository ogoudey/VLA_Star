import threading
import asyncio

class SingleIdentityRunningLock:
    def __init__(self, max_waiters=1):
        self._lock = asyncio.Lock()
        self._cond = asyncio.Condition(self._lock)
        self._active = False
        self._waiting = 0
        self._max_waiters = max_waiters

    async def __aenter__(self):
        print("Outside lock")
        async with self._lock:
            print("Inside lock")

            if self._active:
                if self._waiting >= self._max_waiters:
                    raise RuntimeError("New rerun rejected: too many waiting.")

                self._waiting += 1
                print("Waiting for identity to finish.")
                try:
                    while self._active:
                        await self._cond.wait()
                finally:
                    self._waiting -= 1
            else:
                print("No current identity - ready to run.")

            self._active = True

        return self

    async def __aexit__(self, exc_type, exc, tb):
        async with self._lock:
            self._active = False
            self._cond.notify(1)
