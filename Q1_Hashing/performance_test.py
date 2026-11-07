"""
STEP 6 - performance_test.py   (the experiment for Q1 #4 - run this one too)
============================================================================
Compares search time: HashTable (linear probing) vs ArrayStore (linear search).

For each data size (100, 1,000, 10,000, 50,000 records):
    1. create that many random products (fixed seed -> same data every run)
    2. insert the SAME products, in the SAME order, into both structures
    3. time 3 kinds of search:
         - successful search   : 500 random IDs that exist     (average case)
         - last record         : the product inserted last     (worst case for the array)
         - unsuccessful search : an ID that does not exist
Results are printed and saved to performance_results.csv
"""

import csv
import random
import time
from datetime import date

from array_store import ArrayStore
from hash_table import HashTable
from product import Product

DATA_SIZES = (100, 1_000, 10_000, 50_000)
LOOKUPS = 500           # number of random successful searches per data size
REPEATS = 200           # repeat the single-key searches to get a stable average
SEED = 5022             # fixed random seed -> the experiment can be repeated exactly

CATEGORIES = ["Pain Relief", "Antibiotic", "Allergy", "Gastric",
              "Supplement", "Diabetes", "Cough & Cold", "Hypertension"]
STRENGTHS = ["5mg", "10mg", "20mg", "250mg", "500mg", "1000mg"]


def generate_products(count, rng):
    """Create `count` products with UNIQUE random IDs between 100,000 and 9,999,999."""
    ids = rng.sample(range(100_000, 10_000_000), count)   # sample() never repeats a number
    products = []
    for pid in ids:
        products.append(Product(pid, f"Medicine-{pid}", rng.choice(STRENGTHS), rng.choice(CATEGORIES),
                                round(rng.uniform(2, 200), 2), rng.randint(0, 500),
                                rng.random() < 0.3, date(2028, rng.randint(1, 12), 1)))
    return products


def time_searches(store, keys, repeats=1):
    """Average nanoseconds for ONE search, over all keys (and repeats)."""
    start = time.perf_counter_ns()
    for _ in range(repeats):
        for key in keys:
            store.search(key)
    end = time.perf_counter_ns()
    return (end - start) / (len(keys) * repeats)


def run_experiment():
    rng = random.Random(SEED)
    results = []

    for n in DATA_SIZES:
        products = generate_products(n, rng)

        # Same data, same order, into both structures
        table = HashTable()
        array = ArrayStore()
        for p in products:
            table.insert(p.product_id, p)
            array.insert(p.product_id, p)

        lookup_keys = [p.product_id for p in rng.sample(products, LOOKUPS if n >= LOOKUPS else n)]
        last_key = [products[-1].product_id]   # last inserted -> end of the array
        missing_key = [1]                      # all IDs are >= 100,000, so 1 never exists

        # Check both structures really return the same records
        for k in lookup_keys:
            assert table.search(k) is array.search(k)

        # Average number of probes the hash table needed
        total_probes = 0
        for k in lookup_keys:
            total_probes += table.find_slot(k)[1]
        avg_probes = total_probes / len(lookup_keys)

        results.append({
            "n": n,
            "capacity": table.capacity,
            "load_factor": round(table.load_factor(), 2),
            "avg_probes": round(avg_probes, 2),
            "hash_success_ns": time_searches(table, lookup_keys),
            "array_success_ns": time_searches(array, lookup_keys),
            "hash_last_ns": time_searches(table, last_key, REPEATS),
            "array_last_ns": time_searches(array, last_key, REPEATS),
            "hash_missing_ns": time_searches(table, missing_key, REPEATS),
            "array_missing_ns": time_searches(array, missing_key, REPEATS),
        })
        print(f"  finished n = {n:,}")
    return results


def print_results(results):
    print("\n=== Search Performance: Hash Table (Linear Probing) vs 1-D Array ===")
    print(f"Random successful lookups per size: {LOOKUPS}   |   seed = {SEED}\n")

    print(f"{'Records':>8} | {'Capacity':>8} | {'Load':>5} | {'Avg probes':>10}")
    print("-" * 42)
    for r in results:
        print(f"{r['n']:>8,} | {r['capacity']:>8,} | {r['load_factor']:>5} | {r['avg_probes']:>10}")
    print()

    scenarios = [("Successful search (avg of random IDs)", "success"),
                 ("Worst case for array (last record)", "last"),
                 ("Unsuccessful search (ID not present)", "missing")]
    for title, name in scenarios:
        print(f"--- {title} ---")
        print(f"{'Records':>8} | {'Hash Table (ns)':>16} | {'Array (ns)':>14} | {'Array/Hash':>10}")
        print("-" * 58)
        for r in results:
            h = r[f"hash_{name}_ns"]
            a = r[f"array_{name}_ns"]
            print(f"{r['n']:>8,} | {h:>16,.1f} | {a:>14,.1f} | {a / h:>9,.0f}x")
        print()


def save_csv(results, path="performance_results.csv"):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"Results saved to {path}")


if __name__ == "__main__":
    print("Running experiment (takes a few seconds)...")
    data = run_experiment()
    print_results(data)
    save_csv(data)