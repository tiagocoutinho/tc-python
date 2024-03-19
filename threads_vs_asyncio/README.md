# Threads vs Corotines

Fight!

# Run

```bash
$ python coro.py 10_000
ASYNCIO (N = 10_000; t = 1.0s):
  mem start = 21_737_472

    mem used by coros = 6_029_312 | total = 27_766_784
    mem used by tasks = 6_422_528 | total = 34_189_312
  mem diff during run = 4_456_448 | total = 38_645_760

    mem_end = 37_683_200

time to create coros = 0.005
time to create tasks = 0.037
          total time = 1.100
```

```bash
$ python threaded.py 10_000
THREADS (N = 10_000; t = 5.0s):
  mem start = 15_335_424

  mem used by threads = 23_199_744 | total = 38_535_168
  mem used during run = 158_597_120 | total = 197_132_288

    mem_end = 76_623_872

time to create threads = 0.083
 time to start threads = 2.535
            total time = 7.621
```

## Monitor

```bash
watch -n 0.1 'ps aux | egrep "CPU|coro.py|threaded.py" | grep -v grep'
```


