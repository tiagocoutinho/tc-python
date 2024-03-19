import threading
import time
import sys

import trace


N = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000


def do(t=30):
    time.sleep(t)


def main():
    # on my machine I measured ~2.5s to start a group of 10_000 threads 
    # we're gonna use 1 sec for each 2000 threads we create
    t = N / 2000
    print(f"THREADS ({N = :_}; {t = :.1f}s):")
    with trace.Trace() as trace_global:
        with trace.Trace() as trace_create:
            threads = [threading.Thread(target=do, args=(t,)) for _ in range(N)]
        with trace.Trace() as trace_run:
            [thread.start() for thread in threads]
        [thread.join() for thread in threads]
        #del threads
        #import gc; gc.collect()

    print(f"""\
  mem start = {trace_global.rss_start:_}

  mem used by threads = {trace_create.rss_diff:_} | total = {trace_create.rss_end:_}
  mem used during run = {trace_run.rss_diff:_} | total = {trace_run.rss_end:_}

    mem_end = {trace_global.rss_end:_}

time to create threads = {trace_create.elapsed:.3f}
 time to start threads = {trace_run.elapsed:.3f}
            total time = {trace_global.elapsed:.3f}
""")


if __name__ == "__main__":
    main()
