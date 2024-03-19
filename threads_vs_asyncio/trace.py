import time
import psutil

P = psutil.Process()


def rss():
    return P.memory_info().rss


class Trace:

    def __enter__(self):
        self.time_start = time.monotonic()
        self.rss_start = rss()
        return self

    def __exit__(self, *args):
        self.time_end = time.monotonic()
        self.rss_end = rss()
        self.elapsed = self.time_end - self.time_start
        self.rss_diff = self.rss_end - self.rss_start

    @property
    def dt(self):
        return time.monotonic() - self.time_start

    @property
    def dm(self):
        return rss() - self.rss_start
