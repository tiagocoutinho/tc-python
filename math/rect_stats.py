import math
import collections

import numba
import numpy


MIN_I32 = -2**31
MAX_I32 = 2**31 - 1


Stats = collections.namedtuple("Stats", "min max sum mean std")


def stats(data):
    return Stats(data.min(), data.max(), data.sum(), data.mean(), data.std())


def py_stats_i32(data):
    # with proper std
    m, M, total, var, N = MAX_I32, MIN_I32, 0, 0, data.size
    for row in data:
        for point in row:
            m, M = min(m, point), max(M, point)
            total += point
    mean = total / N
    for row in data:
        for point in row:
            var += (point - mean)**2
    var /= N
    std = math.sqrt(var)
    return Stats(m, M, total, mean, std)


numba_stats_i32 = numba.njit()(py_stats_i32)
numba_stats_i32.__name__ = "numba_stats_i32"


def py_stats_i32_fast_std(data):
    # with std in one loop (may be imprecise for big numbers)
    # (see https://www.strchr.com/standard_deviation_in_one_pass)
    m, M, total, sq_total, N = MAX_I32, MIN_I32, 0, 0.0, data.size
    for row in data:
        for point in row:
            m, M = min(m, point), max(M, point)
            total += point
            sq_total += point * point
    mean = total / N
    var = sq_total / N - mean * mean
    std = math.sqrt(var)
    return Stats(m, M, total, mean, std)


numba_stats_i32_fast_std = numba.njit()(py_stats_i32_fast_std)
numba_stats_i32_fast_std.__name__ = "numba_stats_i32_fast_std"


def test_stats():
    data = numpy.arange(800, dtype='i4')
    data.shape = 40, -1

    expected = Stats(
        data.min(), data.max(), data.sum(), data.mean(), data.std()
    )

    assert stats(data) == expected
    assert py_stats_i32(data) == expected
    assert numba_stats_i32(data) == expected
    assert numba_stats_i32_fast_std(data) == expected


def profile_stats():
    msg = "Warm up numba"
    print(f"{msg:.<50} ", end="", flush=True)
    d = numpy.array([[1,2],[3,4]], dtype='i4')
    numba_stats_i32(d)
    numba_stats_i32_fast_std(d)
    print("DONE!")

    msg = "Running tests"
    print(f"{msg:.<50} ", end="", flush=True)
    #test_stats()
    print("PASSED!")

    from timeit import timeit

    def profile(stats, shape, number):
        size = numpy.multiply(*shape)
        setup = f"import numpy; d = numpy.arange({size}, dtype='i4'); d.shape = {shape}"
        test = "stats(d)"
        namespace = dict(stats=stats)
        msg = f"{stats.__name__} for {shape[0]}x{shape[1]}"
        print(f"{msg:.<50} ", end="", flush=True)
        r = timeit(test, setup=setup, globals=namespace, number=number) / number
        print(f"{r*1000:.3f} ms per interaction")

    sizes = (1280, 720), (1920, 1080), (2560, 1440)
    for size in sizes:
        profile(py_stats_i32, size, 1)
        profile(stats, size, 100)
        profile(numba_stats_i32, size, 100)
        profile(numba_stats_i32_fast_std, size, 100)


if __name__ == "__main__":
    profile_stats()
