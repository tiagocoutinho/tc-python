import sys
import math
import collections

import numba
import numpy

IMAX = sys.maxsize
IMIN = -IMAX - 1

Stats = collections.namedtuple("Stats", "min max sum mean std projection")


def stats(data):
    proj = data.sum(0), data.sum(1)
    return Stats(data.min(), data.max(), proj[0].sum(), data.mean(), data.std(), proj)


def py_stats_int(data):
    # with proper std
    m, M, total, var, N = IMAX, IMIN, 0, 0, data.size
    s0, s1 = data.shape
    k, ex, ex2 = float(data[0][0]), 0.0, 0.0
    proj_0 = numpy.zeros(s0, dtype="i8")
    proj_1 = numpy.zeros(s1, dtype="i8")
    for d0, row in enumerate(data):
        for d1, point in enumerate(row):
            m, M = min(m, point), max(M, point)
            total += point
            proj_0[d0] += point
            proj_1[d1] += point
            # used in std
            p_minus_k = point - k
            ex += p_minus_k
            ex2 += p_minus_k * p_minus_k
    mean = total / N
    var = (ex2 - (ex * ex) / N) / N
    std = math.sqrt(var)
    return Stats(m, M, total, mean, std, (proj_1, proj_0))


numba_stats_int = numba.jit(nopython=True, nogil=True)(py_stats_int)
numba_stats_int.__name__ = "numba_stats_int"


def cmp_stats(s1, s2):
    assert s1[:5] == s2[:5]
    assert (s1.projection[0] == s2.projection[0]).all()
    assert (s1.projection[1] == s2.projection[1]).all()


def test_stats():
    data = numpy.arange(800, dtype="i4")
    data.shape = 40, -1

    expected = Stats(
        data.min(),
        data.max(),
        data.sum(),
        data.mean(),
        data.std(),
        (data.sum(0), data.sum(1)),
    )

    cmp_stats(stats(data), expected)
    cmp_stats(py_stats_int(data), expected)
    cmp_stats(numba_stats_int(data), expected)


def profile_stats():
    msg = "Warm up numba"
    print(f"{msg:.<50} ", end="", flush=True)
    d = numpy.array([[1, 2], [3, 4]], dtype="i4")
    numba_stats_int(d)
    print("DONE!")

    msg = "Running tests"
    print(f"{msg:.<50} ", end="", flush=True)
    test_stats()
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
    dtypes = "i1", "i2", "i4", "i8"

    # Just for reference a pure python
    profile(py_stats_int, (1280, 720), "i4", 1)
    print()
    N = 100
    for size in sizes:
        for dtype in dtypes:
            profile(stats, size, dtype, N)
            profile(numba_stats_int, size, dtype, N)
            print()


if __name__ == "__main__":
    profile_stats()
