"""
STEP 2 - experiment.py
======================
One ROUND of the experiment, two ways:

  run_with_threads()     3 threads, one for each of Fibonacci(35), (38), (40)
  run_without_threads()  the same 3 calls, one after another, in the main thread

Both return a RoundResult with the three answers, the time T in nanoseconds
and the start/end time of each calculation (used to draw the timeline).

  With threads:    T = end of the thread that finished LAST
                     - start of the thread that started FIRST      (the brief's formula)
  Without threads: T = end of the last call - start of the first call
"""

import threading
import time

from fibonacci import fibonacci

FIB_INPUTS = (35, 38, 40)        # the three values required by the brief


def now_ns():
    """Current time in nanoseconds.

    time.perf_counter_ns() is used rather than time.time_ns(): both give
    nanoseconds, but perf_counter_ns() is a high-resolution clock made for
    measuring how long something takes, and it never jumps back if the
    computer's clock is changed while the program runs.
    """
    return time.perf_counter_ns()


class RoundResult:
    """The result of one round."""

    def __init__(self, results, timeline):
        self.results = results              # {35: 9227465, 38: ..., 40: ...}
        self.timeline = timeline            # [(n, start_ns, end_ns), ...]
        first_start = min(start for _, start, _ in timeline)    # t1
        last_end = max(end for _, _, end in timeline)           # t2
        self.first_start = first_start
        self.elapsed_ns = last_end - first_start                # T = t2 - t1



# WITH multithreading
class FibonacciThread(threading.Thread):
    """A thread that works out ONE Fibonacci number and records when it
    started and when it finished."""

    def __init__(self, n, results, lock):
        super().__init__(name=f"Fib-{n}")
        self.n = n
        self.results = results       # one dictionary SHARED by all three threads
        self.lock = lock             # protects the shared dictionary
        self.start_ns = 0
        self.end_ns = 0

    def run(self):
        """What the thread does after start() is called."""
        self.start_ns = now_ns()             # this thread starts working
        value = fibonacci(self.n)
        self.end_ns = now_ns()               # this thread has finished

        # Only ONE thread at a time may write to the shared dictionary,
        # so the shared data always stays correct (no race condition).
        with self.lock:
            self.results[self.n] = value


def run_with_threads(inputs=FIB_INPUTS):
    """One round using a separate thread for every value."""
    results = {}
    lock = threading.Lock()
    threads = [FibonacciThread(n, results, lock) for n in inputs]   # 3 threads

    for t in threads:
        t.start()            # launch all three - they now run at the same time
    for t in threads:
        t.join()             # wait until every thread has finished

    timeline = [(t.n, t.start_ns, t.end_ns) for t in threads]
    return RoundResult(results, timeline)



# WITHOUT multithreading
def run_without_threads(inputs=FIB_INPUTS):
    """One round: the same calculations one after another in the main thread."""
    results = {}
    timeline = []
    for n in inputs:
        start = now_ns()
        results[n] = fibonacci(n)
        timeline.append((n, start, now_ns()))
    return RoundResult(results, timeline)


# Quick test with SMALL numbers, so it finishes at once
if __name__ == "__main__":
    for name, run in (("With threads", run_with_threads), ("Without threads", run_without_threads)):
        r = run((20, 22, 24))
        print(f"{name:<16}: results {r.results} | T = {r.elapsed_ns:,} ns")
        for n, start, end in r.timeline:
            print(f"    Fib({n}) ran from {start - r.first_start:>10,} to {end - r.first_start:>10,} ns")
