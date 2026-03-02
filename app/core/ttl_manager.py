import threading
import time
from typing import Callable


class TTLManager:
    """
    Background TTL cleanup manager.

    Runs a cleanup function periodically to remove expired items.
    Designed to work with in-memory stores (like SessionStore).
    """

    def __init__(
        self,
        cleanup_callback: Callable[[], None],
        interval_seconds: int = 60,
    ):
        """
        :param cleanup_callback: Function to call for cleanup
        :param interval_seconds: How often to run cleanup
        """
        self._cleanup_callback = cleanup_callback
        self._interval = interval_seconds
        self._thread = None
        self._stop_event = threading.Event()

    # =====================================================
    # BACKGROUND LOOP
    # =====================================================

    def _run(self):
        while not self._stop_event.is_set():
            time.sleep(self._interval)
            try:
                self._cleanup_callback()
            except Exception as e:
                # Avoid crashing background thread
                print(f"[TTLManager] Cleanup error: {e}")

    # =====================================================
    # PUBLIC METHODS
    # =====================================================

    def start(self):
        """
        Start background TTL cleanup thread.
        """
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            daemon=True
        )
        self._thread.start()

    def stop(self):
        """
        Stop background TTL cleanup thread.
        """
        self._stop_event.set()
        if self._thread:
            self._thread.join()