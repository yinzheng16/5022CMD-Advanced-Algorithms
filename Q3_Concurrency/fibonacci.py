"""
STEP 1 - fibonacci.py
=====================
The Fibonacci function used in Question 3.

    F(0) = 0,  F(1) = 1,  F(n) = F(n-1) + F(n-2)
    0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55 ...

The plain RECURSIVE version is used on purpose: it does a lot of pure
calculation (Fibonacci(40) makes over 331 million calls), so it takes a few
seconds and the effect of multithreading can be measured clearly.
"""


def fibonacci(n):
    """Return the nth Fibonacci number using recursion.

    Time:  O(2^n)   (exactly: it grows like 1.618^n)
    Space: O(n)     (the deepest chain of calls waiting on the stack)
    """
    if n < 0:                                    # 1 comparison
        raise ValueError("n must be 0 or more")
    if n <= 1:                                   # 1 comparison
        return n                                 # base case: F(0) = 0, F(1) = 1
    return fibonacci(n - 1) + fibonacci(n - 2)   # 2 subtractions, 2 calls, 1 addition


def count_calls(n):
    """How many times fibonacci() runs to work out F(n), WITHOUT running it.

    Every call of fibonacci(n) makes one call of fibonacci(n-1) and one of
    fibonacci(n-2), so:  C(0) = C(1) = 1  and  C(n) = 1 + C(n-1) + C(n-2).
    Worked out with a simple loop, so it is instant even for n = 40.
    It is used in the report to check the Big-O: C(n) = 2 * F(n+1) - 1.
    """
    if n <= 1:
        return 1
    before, current = 1, 1                       # C(0), C(1)
    for _ in range(2, n + 1):
        before, current = current, 1 + current + before
    return current


def counted_fibonacci(n, counter):
    """The same recursion as fibonacci(), but adds 1 to counter[0] on every call.
    Used to COUNT the real number of calls for small n."""
    counter[0] += 1
    if n <= 1:
        return n
    return counted_fibonacci(n - 1, counter) + counted_fibonacci(n - 2, counter)



# Quick test - run this file directly (right-click fibonacci.py -> Run)
if __name__ == "__main__":
    print("First values:", [fibonacci(k) for k in range(11)])
    print()
    print(f"{'n':>3} | {'F(n)':>7} | {'calls counted':>13} | {'2*F(n+1)-1':>10}")
    print("-" * 44)
    for k in (5, 10, 15, 20, 25):
        counter = [0]
        value = counted_fibonacci(k, counter)
        print(f"{k:>3} | {value:>7,} | {counter[0]:>13,} | {2 * fibonacci(k + 1) - 1:>10,}")
    print()
    for k in (35, 38, 40):
        print(f"fibonacci({k}) makes {count_calls(k):,} calls")
