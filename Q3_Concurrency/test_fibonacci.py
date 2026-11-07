"""
STEP 7 - test_fibonacci.py  -  automatic tests for Question 3
=============================================================
Run it like any other file (right-click -> Run). Small Fibonacci numbers are
used so the tests finish in under a second.
"""

import threading
import unittest

from experiment import FibonacciThread, run_with_threads, run_without_threads
from fibonacci import count_calls, counted_fibonacci, fibonacci


class TestFibonacci(unittest.TestCase):

    def __str__(self):
        return self._testMethodName          # show only the test name in the output

    def test_first_values(self):
        self.assertEqual([fibonacci(n) for n in range(11)], [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])

    def test_known_large_value(self):
        self.assertEqual(fibonacci(25), 75025)

    def test_negative_number_is_rejected(self):
        with self.assertRaises(ValueError):
            fibonacci(-1)

    def test_call_count_formula(self):
        # the real number of calls equals 2 * F(n+1) - 1 (used for the Big-O)
        for n in range(0, 21):
            counter = [0]
            counted_fibonacci(n, counter)
            self.assertEqual(counter[0], 2 * fibonacci(n + 1) - 1)
            self.assertEqual(count_calls(n), counter[0])


class TestExperiment(unittest.TestCase):

    def __str__(self):
        return self._testMethodName

    INPUTS = (15, 18, 20)                    # small, so the tests are fast

    def test_threads_give_correct_results(self):
        r = run_with_threads(self.INPUTS)
        self.assertEqual(r.results, {15: 610, 18: 2584, 20: 6765})

    def test_without_threads_gives_same_results(self):
        self.assertEqual(run_without_threads(self.INPUTS).results, run_with_threads(self.INPUTS).results)

    def test_three_separate_threads_are_used(self):
        seen = set()
        original_run = FibonacciThread.run

        def spy(self_thread):
            seen.add(threading.get_ident())   # the id of the thread running this code
            original_run(self_thread)

        FibonacciThread.run = spy
        try:
            run_with_threads(self.INPUTS)
        finally:
            FibonacciThread.run = original_run
        self.assertEqual(len(seen), 3)
        self.assertNotIn(threading.main_thread().ident, seen)

    def test_elapsed_time_is_t2_minus_t1(self):
        r = run_with_threads(self.INPUTS)
        t1 = min(start for _, start, _ in r.timeline)
        t2 = max(end for _, _, end in r.timeline)
        self.assertEqual(r.elapsed_ns, t2 - t1)
        self.assertGreater(r.elapsed_ns, 0)

    def test_sequential_calls_do_not_overlap(self):
        timeline = run_without_threads(self.INPUTS).timeline
        for (_, _, end), (_, next_start, _) in zip(timeline, timeline[1:]):
            self.assertLessEqual(end, next_start)


if __name__ == "__main__":
    unittest.main(verbosity=2)        # verbosity=2 prints the name of every test
