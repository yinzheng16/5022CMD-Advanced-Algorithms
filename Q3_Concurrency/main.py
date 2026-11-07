"""
STEP 5 - main.py   (THE MAIN PROGRAM - run this one)
====================================================
Fibonacci experiment: WITH and WITHOUT multithreading.

Menu
  1. Run the full experiment (10 rounds with threads, 10 rounds without)   <- the brief
  2. Run a quick experiment (choose 1-10 rounds, for a demo)
  3. View the last round as a timeline (when each calculation ran)
  4. Check the Big-O: count the calls made by fibonacci(n)
  5. Extra: I/O-bound task with threads (where threads DO help)
  6. Extra: the same Fibonacci job with multiprocessing
  7. Exit

The full experiment takes several minutes, because Fibonacci(40) alone makes
over 331 million calls. Results are also saved to experiment_results.csv.
"""

import csv
import sys

from display import SEPARATOR, pause, print_box, print_table, print_title
from experiment import FIB_INPUTS, run_with_threads, run_without_threads
from extra_demos import FILES, DOWNLOAD_SECONDS, cpu_cores, io_bound_demo, multiprocessing_demo
from fibonacci import count_calls, counted_fibonacci, fibonacci
from timeline import timeline_lines

ROUNDS = 10                              # the brief asks for 10 rounds
RESULTS_FILE = "experiment_results.csv"

last_rounds = {}                         # remembers the last experiment for option 3



# Small helpers
def ns(value):
    """12345678901 -> '12,345,678,901 ns'"""
    return f"{value:,} ns"


def seconds(value):
    return f"{value / 1e9:.3f} s"


def gil_status():
    check = getattr(sys, "_is_gil_enabled", None)
    return True if check is None else check()


def ask_rounds():
    while True:
        try:
            value = int(input("How many rounds (1-10)? "))
            if 1 <= value <= ROUNDS:
                return value
        except ValueError:
            pass
        print("  Please enter a number from 1 to 10.")



# The experiment
def run_experiment(title, run_round, rounds):
    """Run `run_round` for the given number of rounds, print a live line per
    round, then a table. Returns the list of RoundResult."""
    print_title(f"FIBONACCI {', '.join(str(n) for n in FIB_INPUTS)}  -  {title.upper()}")
    results = []
    for r in range(1, rounds + 1):
        print(f"  Round {r:>2}/{rounds} running ...", end="", flush=True)
        result = run_round()
        results.append(result)
        print(f"\r  Round {r:>2}/{rounds} done: T = {ns(result.elapsed_ns):>20}  ({seconds(result.elapsed_ns)})")

    first = results[0].results
    print(f"  Results: " + ", ".join(f"Fib({n}) = {first[n]:,}" for n in FIB_INPUTS))
    rows = [[i, ns(r.elapsed_ns), seconds(r.elapsed_ns)] for i, r in enumerate(results, start=1)]
    times = [r.elapsed_ns for r in results]
    average = sum(times) // len(times)
    rows.append(["Average", ns(average), seconds(average)])
    print_table(["Round", "Time taken T", "Seconds"], rows, right_align=(0, 1, 2))
    print(f"  Fastest: {ns(min(times))}   Slowest: {ns(max(times))}")
    return results


def compare(with_threads, without_threads):
    """The final comparison box."""
    avg_with = sum(r.elapsed_ns for r in with_threads) // len(with_threads)
    avg_without = sum(r.elapsed_ns for r in without_threads) // len(without_threads)
    change = (avg_with - avg_without) / avg_without * 100
    if change > 0:
        verdict = f"Multithreading was {change:.1f}% SLOWER on average."
    else:
        verdict = f"Multithreading was {-change:.1f}% FASTER on average."
    print()
    print_box("COMPARISON", [
        f"Average T with multithreading    : {ns(avg_with):>22}  ({seconds(avg_with)})",
        f"Average T without multithreading : {ns(avg_without):>22}  ({seconds(avg_without)})",
        SEPARATOR,
        verdict,
        SEPARATOR,
        f"CPU cores: {cpu_cores()}   |   Python {sys.version.split()[0]}   |   GIL enabled: {gil_status()}",
    ])


def save_results(with_threads, without_threads):
    """Save every round to a CSV file (used by make_chart.py)."""
    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["round", "with_threads_ns", "without_threads_ns"])
        for i, (a, b) in enumerate(zip(with_threads, without_threads), start=1):
            writer.writerow([i, a.elapsed_ns, b.elapsed_ns])
    with open("timeline_last_round.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["mode", "n", "start_ns", "end_ns"])
        for mode, r in (("with threads", with_threads[-1]), ("without threads", without_threads[-1])):
            for n, start, end in r.timeline:
                writer.writerow([mode, n, start - r.first_start, end - r.first_start])
    print(f"  Results saved to {RESULTS_FILE} and timeline_last_round.csv")


def experiment(rounds):
    print(f"Running {rounds} round(s) each way. Please wait - this can take a few minutes.\n")
    with_threads = run_experiment("with multithreading", run_with_threads, rounds)
    print()
    without_threads = run_experiment("without multithreading", run_without_threads, rounds)
    compare(with_threads, without_threads)
    save_results(with_threads, without_threads)
    last_rounds["with"] = with_threads[-1]
    last_rounds["without"] = without_threads[-1]


# Menu options
def full_experiment():
    """Option 1 - exactly what the brief asks for: 10 rounds each way."""
    experiment(ROUNDS)


def quick_experiment():
    """Option 2 - fewer rounds, for a quick demonstration."""
    experiment(ask_rounds())


def view_timeline():
    """Option 3 - the last round of each experiment as a bar timeline."""
    if not last_rounds:
        print("Run an experiment first (option 1 or 2).")
        return
    for key, title in (("with", "WITH MULTITHREADING"), ("without", "WITHOUT MULTITHREADING")):
        r = last_rounds[key]
        print_box(f"LAST ROUND {title}", timeline_lines(r) + [SEPARATOR, f"T = t2 - t1 = {ns(r.elapsed_ns)}"])


def big_o_check():
    """Option 4 - real call counts compared with the formula 2*F(n+1) - 1."""
    rows = []
    for n in (5, 10, 15, 20, 25):
        counter = [0]
        counted_fibonacci(n, counter)
        rows.append([n, f"{counter[0]:,}", f"{2 * fibonacci(n + 1) - 1:,}",
                     "yes" if counter[0] == 2 * fibonacci(n + 1) - 1 else "NO"])
    print_title("BIG-O CHECK: NUMBER OF CALLS")
    print_table(["n", "Calls counted", "2*F(n+1) - 1", "Match"], rows, right_align=(0, 1, 2))
    lines = []
    previous = None
    for n in (35, 38, 40):
        calls = count_calls(n)
        growth = f"   ({calls / previous:.2f}x the line above)" if previous else ""
        lines.append(f"fibonacci({n}) makes {calls:>12,} calls{growth}")
        previous = calls
    lines += [SEPARATOR, "Each +1 in n multiplies the work by about 1.618 (the golden ratio).",
              "So the time grows exponentially: O(2^n), more exactly Theta(1.618^n)."]
    print_box("CALLS FOR THE VALUES IN THE EXPERIMENT", lines)


def io_demo():
    """Option 5 - threads DO help when the work is waiting (I/O)."""
    print(f"Downloading {len(FILES)} files, each takes {DOWNLOAD_SECONDS:.0f} s of waiting ...")
    seq, thr = io_bound_demo()
    print_box("I/O-BOUND TASK (SIMULATED DOWNLOADS)", [
        f"Without multithreading : {ns(seq):>18}  ({seconds(seq)})",
        f"With multithreading    : {ns(thr):>18}  ({seconds(thr)})",
        SEPARATOR,
        f"Multithreading was {seq / thr:.1f}x FASTER: the waits overlap.",
    ])


def process_demo():
    """Option 6 - multiprocessing can use several CPU cores for the Fibonacci job."""
    print(f"Running Fibonacci{FIB_INPUTS} in 1 process, then in 3 processes ...")
    seq, par, results = multiprocessing_demo()
    print_box(f"MULTIPROCESSING ({cpu_cores()} CPU cores)", [
        f"One process (no parallelism) : {ns(seq):>22}  ({seconds(seq)})",
        f"Three processes (parallel)   : {ns(par):>22}  ({seconds(par)})",
        SEPARATOR,
        f"Results: {results}",
        f"Multiprocessing was {seq / par:.2f}x faster.",
    ])


MENU = [
    ("Run the Full Experiment (10 rounds each)", full_experiment),
    ("Run a Quick Experiment (choose rounds)", quick_experiment),
    ("View the Last Round as a Timeline", view_timeline),
    ("Check the Big-O (count the calls)", big_o_check),
    ("Extra: I/O-Bound Task with Threads", io_demo),
    ("Extra: Fibonacci with Multiprocessing", process_demo),
]


def main():
    exit_option = str(len(MENU) + 1)
    while True:
        print()
        lines = [f"Fibonacci{FIB_INPUTS}  |  {cpu_cores()} CPU cores  |  GIL enabled: {gil_status()}", SEPARATOR]
        lines += [f"  {i}. {text}" for i, (text, _) in enumerate(MENU, start=1)]
        lines += [SEPARATOR, f"  {exit_option}. Exit"]
        print_box("FIBONACCI MULTITHREADING EXPERIMENT", lines)

        choice = ""
        while choice == "":
            choice = input("Enter choice: ").strip()
        if choice == exit_option:
            print("\nExiting program. Goodbye!")
            break
        if choice.isdigit() and 1 <= int(choice) <= len(MENU):
            print()
            MENU[int(choice) - 1][1]()
            pause()
        else:
            print(f"Invalid choice, please enter 1-{exit_option}.")


# This guard is REQUIRED for multiprocessing on Windows: each new process
# imports this file, and must not start the menu again.
if __name__ == "__main__":
    main()
