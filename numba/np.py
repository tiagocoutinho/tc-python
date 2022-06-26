import numpy as np
from timeit import default_timer as timer

def main():
    vec_size = 500_000_000

    print("preparing...")
    a = b = np.array(np.random.sample(vec_size), dtype=np.float32)
    c = np.zeros(vec_size, dtype=np.float32)

    print("starting...")
    start = timer()
    np.power(a, b, c)
    duration = timer() - start

    print(duration)

if __name__ == '__main__':
    main()
