import numpy
from timeit import default_timer
from numba import jit, prange, vectorize, guvectorize, float32


class Chrono:
    def __init__(self, message):
        self.message = message
    def __enter__(self):
        print(f"{self.message:.<80}", end="", flush=True)
        self.start = default_timer()
    def __exit__(self, exc_type, exc_value, tb):
        self.time = default_timer() - self.start
        print(f"[DONE] Took {self.time*1000:.3f} ms")


def python_power(a, b, c):
    for i in range(a.size):
         c[i] = a[i] ** b[i]


numpy_power = numpy.power


@vectorize([float32(float32, float32)], target='cpu')
def numba_vectorize_power(a, b):
    return a ** b


#@guvectorize([(float32[:], float32[:], float32[:])], '(n),(n)->(n)')
#def numba_guvectorize_power(a, b, c):
#    for i in range(a.size):
#        c[i] = a[i] ** b[i]
numba_guvectorize_power = \
  guvectorize([(float32[:], float32[:], float32[:])], '(n),(n)->(n)')(python_power)


numba_jit_power = jit(nopython=True)(python_power)


@jit(nopython=True, parallel=True)
def numba_jit_parallel_power(a, b, c):
    for i in prange(a.size):
         c[i] = a[i] ** b[i]



def main():
    vec_size = 200_000_000

    with Chrono("Prepare"):
        dtype = numpy.float32
        a = numpy.array(numpy.random.sample(vec_size), dtype=dtype)
        b = numpy.array(numpy.random.sample(vec_size), dtype=dtype)
        c = numpy.zeros(vec_size, dtype=dtype)

    '''
    with Chrono("pure python"):
        python_power(a, b, c)

    with Chrono("numpy alloc result"):
        numpy_power(a, b)

    with Chrono("numpy"):
        numpy_power(a, b, c)

    with Chrono("numpy broadcast alloc result"):
        _ = a ** b

    with Chrono("numba vectorize alloc result"):
        numba_vectorize_power(a, b)

    with Chrono("numba gu vectorize"):
        numba_guvectorize_power(a, b, c)

    '''
    with Chrono("numba jit"):
        numba_jit_power(a, b, c)

    with Chrono("numba jit parallel"):
        numba_jit_parallel_power(a, b, c)

    numba_jit_parallel_power.parallel_diagnostics(level=4)


if __name__ == '__main__':
    main()
