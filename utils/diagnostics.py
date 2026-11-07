"""Performance and diagnostics monitor (FPS, latency, frame times)."""
import time
from collections import deque

class Diagnostics:
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self._timestamps = deque(maxlen=window_size)
        self._latencies = deque(maxlen=window_size)
        self.fps = 0.0
        self.avg_latency_ms = 0.0

    def record_frame(self, latency_ms: float = 0.0):
        now = time.time()
        self._timestamps.append(now)
        self._latencies.append(latency_ms)

        if len(self._timestamps) > 1:
            total_duration = self._timestamps[-1] - self._timestamps[0]
            if total_duration > 0:
                self.fps = (len(self._timestamps) - 1) / total_duration

        if self._latencies:
            self.avg_latency_ms = sum(self._latencies) / len(self._latencies)

