import numpy as np
import time

def time_benchmark(iterations = (64,3)):
    # Inicjalizacja macierzy 8x8
    matrix = np.random.randint(0, 5, size=(8, 8), dtype=np.int8)

    itt = iterations[0] ** iterations[1]

    start = time.time()
    for i in range(itt):
        np.sum(matrix)

    end = time.time()
    elapsed = end - start

    return elapsed