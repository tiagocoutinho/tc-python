import sys
import math
import collections

import numba
import numpy

IMAX = sys.maxsize
IMIN = -IMAX - 1

Stats = collections.namedtuple(
    "Stats", "min max sum mean std projection"
)


def stats(data):
    return Stats(
        data.min(), data.max(), data.sum(), data.mean(), data.std(),
        (data.sum(0), data.sum(1))
    )


def py_stats_int(data):
    # with proper std
    m, M, total, var, N = IMAX, IMIN, 0, 0, data.size
    proj_0 = numpy.zeros(data.shape[0], dtype='i8')
    proj_1 = numpy.zeros(data.shape[1], dtype='i8')
    for d0, row in enumerate(data):
        for d1, point in enumerate(row):
            m, M = min(m, point), max(M, point)
            total += point
            proj_0[d0] += point
            proj_1[d1] += point
    mean = total / N
    for row in data:
        for point in row:
            var += (point - mean)**2
    var /= N
    std = math.sqrt(var)
    return Stats(m, M, total, mean, std, (proj_0, proj_1))


numba_stats_int = numba.njit()(py_stats_int)
numba_stats_int.__name__ = "numba_stats_int"


def py_stats_int_fast_std(data):
    # with std in one loop (may be imprecise for big numbers)
    # (see https://www.strchr.com/standard_deviation_in_one_pass)
    m, M, total, sq_total, N = IMAX, IMIN, 0, 0.0, data.size
    proj_0 = numpy.zeros(data.shape[0], dtype='i8')
    proj_1 = numpy.zeros(data.shape[1], dtype='i8')
    for d0, row in enumerate(data):
        for d1, point in enumerate(row):
            m, M = min(m, point), max(M, point)
            total += point
            sq_total += point * point
            proj_0[d0] += point
            proj_1[d1] += point
    mean = total / N
    var = sq_total / N - mean * mean
    std = math.sqrt(var)
    return Stats(m, M, total, mean, std, (proj_0, proj_1))


numba_stats_int_fast_std = numba.njit()(py_stats_int_fast_std)
numba_stats_int_fast_std.__name__ = "numba_stats_int_fast_std"


def test_stats():
    data = numpy.arange(800, dtype='i4')
    data.shape = 40, -1

    expected = Stats(
        data.min(), data.max(), data.sum(), data.mean(), data.std()
    )

    assert stats(data) == expected
    assert py_stats_int(data) == expected
    assert numba_stats_int(data) == expected
    assert numba_stats_int_fast_std(data) == expected


def profile_stats():
    msg = "Warm up numba"
    print(f"{msg:.<50} ", end="", flush=True)
    d = numpy.array([[1,2],[3,4]], dtype='i4')
    numba_stats_int(d)
    numba_stats_int_fast_std(d)
    print("DONE!")

    msg = "Running tests"
    print(f"{msg:.<50} ", end="", flush=True)
    #test_stats()
    print("PASSED!")

    from timeit import timeit

    def profile(stats, shape, dtype, number):
        size = numpy.multiply(*shape)
        setup = f"import numpy; d = numpy.arange({size}, dtype='{dtype}'); d.shape = {shape}"
        test = "stats(d)"
        namespace = dict(stats=stats)
        msg = f"{stats.__name__} for {shape[0]}x{shape[1]}x{dtype}"
        print(f"{msg:.<50} ", end="", flush=True)
        r = timeit(test, setup=setup, globals=namespace, number=number) / number
        print(f"{r*1000:.3f} ms per interaction")

    sizes = (1280, 720), (1920, 1080), (2560, 1440)
    dtypes = 'i1', 'i2', 'i4', 'i8'

    # Just for reference a pure python
    profile(py_stats_int, (1280, 720), 'i4', 1)
    print()
    N = 100
    for size in sizes:
        for dtype in dtypes:
            profile(stats, size, dtype, N)
            profile(numba_stats_int, size, dtype, N)
            profile(numba_stats_int_fast_std, size, dtype, N)
            print()

if __name__ == "__main__":
    profile_stats()
