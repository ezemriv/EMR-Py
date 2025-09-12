# src/emrpy/decorators.py
"""
Function Decorators

Execution profiling utilities for measuring runtime and memory usage.
"""

import time
import tracemalloc


def timer_and_memory(func):
    """
    Decorator to measure execution time and peak memory usage of a function.

    Uses `tracemalloc` to track memory allocations and prints both runtime and
    peak memory in megabytes after function execution.

    Parameters:
    -----------
    func : Callable
        The function to profile.

    Returns:
    --------
    Callable
        Wrapped function that prints runtime and memory usage on each call.

    Examples:
    ---------
    >>> @timer_and_memory
    ... def compute():
    ...     data = [x**2 for x in range(10**6)]

    >>> compute()
    Function 'compute' executed in 0.12 seconds and Peak memory usage: 45.231 MB.
    """

    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(
            f"""
            Function '{func.__name__}' executed in {end_time - start_time:.2f} seconds
            and Peak memory usage: {peak / 10**6:.3f} MB.
            """
        )
        return result

    return wrapper


def timer(func):
    """
    Decorator to measure and print the execution time of a function.

    Parameters:
    -----------
    func : Callable
        The function to time.

    Returns:
    --------
    Callable
        Wrapped function that prints execution duration on each call.

    Examples:
    ---------
    >>> @timer
    ... def slow_fn():
    ...     time.sleep(2)

    >>> slow_fn()
    Function 'slow_fn' executed in 2.00 seconds.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function '{func.__name__}' executed in {end_time - start_time:.2f} seconds.")
        return result

    return wrapper
