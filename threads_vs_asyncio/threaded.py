import threading
import time
import sys

from trace import Trace, mem

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000

def do(t):
    time.sleep(t)

def main():
    # on my machine I measured ~2.5s to start a group of 10_000 threads
    # we're gonna use 1 sec for each 1000 threads we create
    t = N / 1000
    print(f"THREADS ({N = :_}; {t = :.1f}s):")
    with Trace() as trace_global:
        with Trace() as trace_create:
            threads = [threading.Thread(target=do, args=(t,)) for _ in range(N)]
        
        with Trace() as trace_run:
            [thread.start() for thread in threads]
        [thread.join() for thread in threads]

        #del threads
        #import gc; gc.collect()

    print(f"""\
  mem start = {mem(trace_global.rss_start)}

  mem used by threads = {mem(trace_create.rss_diff)} | total = {mem(trace_create.rss_end)}
  mem used during run = {mem(trace_run.rss_diff)} | total = {mem(trace_run.rss_end)}

    mem_end = {mem(trace_global.rss_end)}

time to create threads = {trace_create.elapsed:.3f}
 time to start threads = {trace_run.elapsed:.3f}
            total time = {trace_global.elapsed:.3f}
""")


if __name__ == "__main__":
    main()
