import asyncio
import sys

import trace


N = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000

def do(t=6):
    return asyncio.sleep(t)


async def main():
    # on my machine I measured ~0.05s to start a group of 10_000 tasks 
    # we're gonna use 1 sec for each 10_000 tasks we create
    t = N / 10_000
    print(f"ASYNCIO ({N = :_}; {t = :.1f}s):")
    with trace.Trace() as trace_global:
        with trace.Trace() as trace_coros:
            coros = [do(t) for _ in range(N)]

        with trace.Trace() as trace_tasks:
            tasks = [asyncio.create_task(coro) for coro in coros]

        with trace.Trace() as trace_run:
            await asyncio.sleep(0.1)

        for task in tasks:
            await task
        
        #del coros
        #del tasks
        #import gc; gc.collect()

    print(f"""\
  mem start = {trace_global.rss_start:_}

    mem used by coros = {trace_coros.rss_diff:_} | total = {trace_coros.rss_end:_}
    mem used by tasks = {trace_tasks.rss_diff:_} | total = {trace_tasks.rss_end:_}
  mem diff during run = {trace_run.rss_diff:_} | total = {trace_run.rss_end:_}

    mem_end = {trace_global.rss_end:_}

time to create coros = {trace_coros.elapsed:.3f}
time to create tasks = {trace_tasks.elapsed:.3f}
          total time = {trace_global.elapsed:.3f}
""")


if __name__ == "__main__":
    asyncio.run(main())
