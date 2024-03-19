import asyncio
import sys

from trace import Trace, mem

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000

def do(t):
    return asyncio.sleep(t)

async def main():
    # on my machine I measured ~0.05s to start a group of 10_000 tasks 
    # we're gonna use 1 sec for each 1_000 tasks we create
    t = N / 1000
    print(f"ASYNCIO ({N = :_}; {t = :.1f}s):")
    with Trace() as trace_global:
        with Trace() as trace_coros:
            coros = [do(t) for _ in range(N)]

        with Trace() as trace_tasks:
            tasks = [asyncio.create_task(coro) for coro in coros]

        with Trace() as trace_run:
            await asyncio.sleep(0.1)

        for task in tasks:
            await task
        
        #del coros
        #del tasks
        #import gc; gc.collect()

    print(f"""\
  mem start = {mem(trace_global.rss_start)}

    mem used by coros = {mem(trace_coros.rss_diff)} | total = {mem(trace_coros.rss_end)}
    mem used by tasks = {mem(trace_tasks.rss_diff)} | total = {mem(trace_tasks.rss_end)}
  mem diff during run = {mem(trace_run.rss_diff)} | total = {mem(trace_run.rss_end)}

    mem_end = {mem(trace_global.rss_end)}

time to create coros = {trace_coros.elapsed:.3f}
time to create tasks = {trace_tasks.elapsed:.3f}
          total time = {trace_global.elapsed:.3f}
""")


if __name__ == "__main__":
    asyncio.run(main())
