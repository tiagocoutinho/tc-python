import numpy

from rect_stats import Stats, stats, py_stats_int, numba_stats_int, jax_stats_int


def test_stats():

    def cmp_stats(s1, s2):
        assert numpy.isclose(s1[:5], s2[:5]).all()
        assert (s1.projection[0] == s2.projection[0]).all()
        assert (s1.projection[1] == s2.projection[1]).all()

    data = numpy.arange(800, dtype="i4")
    data.shape = 40, -1

    expected = Stats(
        data.min(),
        data.max(),
        data.sum(),
        data.mean(),
        data.std(),
        (data.sum(1), data.sum(0)),
    )

    cmp_stats(stats(data), expected)
    cmp_stats(py_stats_int(data), expected)
    cmp_stats(numba_stats_int(data), expected)
    if jax_stats_int:
        cmp_stats(jax_stats_int(data), expected)


def profile_stats():
    sizes = (1280, 720), (1920, 1080), (2560, 1440)
    dtypes = "i1", "i2", "i4", "i8"

    msg = "Warm up numba"
    print(f"{msg:.<50} ", end="", flush=True)
    for dtype in dtypes:
        d = numpy.array([[1, 2], [3, 4]], dtype=dtype)
        stats(d)
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

    profile(numba_stats_int, (10000, 5000), "i4", 100)

    # Just for reference a pure python
    profile(py_stats_int, (1280, 720), "i4", 1)
    print()
    N = 100
    for size in sizes:
        for dtype in dtypes:
            profile(stats, size, dtype, N)
            profile(numba_stats_int, size, dtype, N)
            if jax_stats_int:
                profile(jax_stats_int, size, dtype, N)
            print()


if __name__ == "__main__":
    profile_stats()
