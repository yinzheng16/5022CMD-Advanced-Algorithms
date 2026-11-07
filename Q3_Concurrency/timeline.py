"""
STEP 3 - timeline.py
====================
Draws ONE round as a timeline in the console, so you can SEE when each
calculation was running:

  WITH threads (all start together, finish one by one):
    Fib(35) |█████                                   |
    Fib(38) |█████████████████                       |
    Fib(40) |████████████████████████████████████████|
            t1                                       t2

  WITHOUT threads (one after another):
    Fib(35) |███                                     |
    Fib(38) |   ████████████                         |
    Fib(40) |               █████████████████████████|
"""

BAR_WIDTH = 44           # number of characters between | and |


def timeline_lines(result, width=BAR_WIDTH):
    """Lines of text for a bar timeline of one RoundResult.
    Every bar is placed on the same scale: 0 = t1, width = t2."""
    total = result.elapsed_ns or 1
    lines = []
    for n, start, end in result.timeline:
        a = round((start - result.first_start) / total * width)   # where the bar starts
        b = round((end - result.first_start) / total * width)     # where the bar ends
        b = max(b, a + 1)                                          # at least one block
        bar = " " * a + "█" * (b - a) + " " * (width - b)
        seconds = (end - start) / 1e9
        lines.append(f"Fib({n}) |{bar}| {seconds:5.2f} s")
    lines.append(f"{'':8}t1{'':{width - 2}}t2")
    return lines


# Quick test with small numbers
if __name__ == "__main__":
    from experiment import run_with_threads, run_without_threads
    print("With threads:")
    print("\n".join(timeline_lines(run_with_threads((22, 24, 26)))))
    print("\nWithout threads:")
    print("\n".join(timeline_lines(run_without_threads((22, 24, 26)))))
