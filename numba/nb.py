import numpy as np
from timeit import default_timer as timer
from numba import vectorize

@vectorize(['float32(float32, float32)'], target='cpu')
def pow(a, b):
    return a ** b

def main():
    vec_size = 500_000_000

    print("preparing...")
    a = b = np.array(np.random.sample(vec_size), dtype=np.float32)

    print("warm up...")
    warm = np.array(np.random.sample(1000), dtype=np.float32)
    c = pow(warm, warm)

    print("starting...")
    start = timer()
    c = pow(a, b)
    duration = timer() - start

    print(duration)

if __name__ == '__main__':
    main()
