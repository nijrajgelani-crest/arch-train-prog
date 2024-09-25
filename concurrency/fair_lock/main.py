import time
import threading

from threading import Lock
from queue import Queue


class LegalRentrantLock:
    """A fair and legal lock implementation."""

    def __init__(self):
        # use the reentrant lock as the underlying lock
        self._lock = Lock()
        self._queue_lock = Lock()
        self._entrancy_lock = Lock()
        self._entrancy_count = 0
        self._current_thread = None
        # queue to manage threads waiting for the lock
        self._wait_queue = Queue()

    def acquire(self, blocking=True, timeout=-1) -> bool:
        """Acquire the lock.

        Args:
            blocking (bool, optional): Block until the lock can be acquired.
            Defaults to True.
            timeout (int, optional): Number of seconds to wait for the lock.
            Defaults to -1.

        Returns:
            bool: True if the lock was acquired, False otherwise.
        """
        print(f"Trying to acquire for {threading.current_thread().ident}...")
        with self._entrancy_lock:
            if (
                self._entrancy_count > 0
                and self._current_thread == threading.current_thread().ident
            ):
                self._entrancy_count += 1
                print(
                    f"{threading.current_thread().ident} is already holding "
                    f"the lock..."
                )
                return True
        with self._queue_lock:
            self._wait_queue.put(threading.current_thread().ident)

            print(f"Added {threading.current_thread().ident} to queue...")
        while (
            self._wait_queue.queue[0] is not threading.current_thread().ident
        ):
            print(f"Waiting for {self._wait_queue.queue[0]} to release...")
            time.sleep(0.1)
        with self._entrancy_lock:
            self._entrancy_count += 1
            self._current_thread = threading.current_thread().ident
            return self._lock.acquire(blocking, timeout)

    def release(self):
        """Release the lock."""
        print(f"Release called by {threading.current_thread().ident}...")
        with self._entrancy_lock:

            print(f"Releasing {threading.current_thread().ident}...")
            self._entrancy_count -= 1
            if self._entrancy_count == 0:
                self._current_thread = None

                with self._queue_lock:
                    self._wait_queue.get()
                return self._lock.release()

    def __enter__(self):
        """Acquire the lock."""
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release the lock."""
        self.release()


# Example usage

counter = 0
mutex = LegalRentrantLock()


def increment():
    global counter
    for _ in range(3):
        with mutex:
            print("inc start")
            time.sleep(1)
            with mutex:
                counter += 1
            print("inc end")


for i in range(1):
    counter = 0
    t = threading.Thread(target=increment)
    t2 = threading.Thread(target=increment)
    t.start()
    t2.start()
    t2.join()
    t.join()

    print(f"Attempt - {i+1} - Final Counter:", counter)
