"""
STEP 4 - extra_demos.py
=======================
Two extra experiments for the discussion in the report:

Demo A - an I/O-BOUND task, where multithreading DOES help.
         Three simulated downloads that each wait 1 second. While a thread
         is waiting for I/O it gives up the GIL, so the waits overlap.

Demo B - the same CPU-bound Fibonacci job with MULTIPROCESSING.
         Each process has its own Python interpreter and its own GIL, so the
         calculations can run in PARALLEL on different CPU cores.
"""

import multiprocessing
import os
import threading
import time

from fibonacci import fibonacci

DOWNLOAD_SECONDS = 1.0
FILES = ["timetable.pdf", "results.csv", "photo.jpg"]


def simulated_download(file_name):
    """Pretend to download a file: the thread just WAITS, like waiting for a network."""
    time.sleep(DOWNLOAD_SECONDS)


def io_bound_demo():
    """Returns (time without threads, time with threads) in nanoseconds."""
    start = time.perf_counter_ns()
    for f in FILES:                                   # one after another
        simulated_download(f)
    sequential = time.perf_counter_ns() - start

    start = time.perf_counter_ns()
    threads = [threading.Thread(target=simulated_download, args=(f,)) for f in FILES]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    threaded = time.perf_counter_ns() - start
    return sequential, threaded


def multiprocessing_demo(inputs=(35, 38, 40)):
    """Returns (time in one process, time with one process per value, results) in ns."""
    start = time.perf_counter_ns()
    for n in inputs:
        fibonacci(n)
    sequential = time.perf_counter_ns() - start

    start = time.perf_counter_ns()
    with multiprocessing.Pool(processes=len(inputs)) as pool:   # 3 separate processes
        results = pool.map(fibonacci, inputs)
    parallel = time.perf_counter_ns() - start
    return sequential, parallel, results


def cpu_cores():
    return os.cpu_count()


# Quick test (Demo A only - it takes 4 seconds)
if __name__ == "__main__":
    seq, thr = io_bound_demo()
    print(f"I/O-bound: without threads {seq:,} ns | with threads {thr:,} ns | {seq / thr:.1f}x faster")
