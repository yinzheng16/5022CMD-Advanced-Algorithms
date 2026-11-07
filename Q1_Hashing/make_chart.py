"""
make_chart.py  -  draw the graph for the Q1 report (optional)
=============================================================
Reads performance_results.csv (made by performance_test.py) and saves
search_performance_chart.png.

Needs the matplotlib library. Install it once in PyCharm:
    File -> Settings -> Project -> Python Interpreter -> "+" -> search "matplotlib" -> Install
or in the PyCharm Terminal:   pip install matplotlib

Both axes are LOGARITHMIC (each step is 10x bigger), so a straight rising
line means the time grows in proportion to n - O(n) - and a flat line
means the time does not depend on n - O(1).
"""

import csv

import matplotlib.pyplot as plt

CSV_FILE = "performance_results.csv"
CHART_FILE = "search_performance_chart.png"

# Read the results saved by performance_test.py
with open(CSV_FILE) as f:
    rows = list(csv.DictReader(f))

n = [int(r["n"]) for r in rows]


def column(name):
    return [float(r[name]) for r in rows]


plt.figure(figsize=(7, 3.8), dpi=200)
plt.plot(n, column("array_success_ns"), "o-", color="#C55A11", label="Array – linear search, O(n)")
plt.plot(n, column("array_missing_ns"), "o--", color="#C55A11", alpha=0.55, label="Array – ID not present")
plt.plot(n, column("hash_success_ns"), "s-", color="#2E74B5", label="Hash table – linear probing, O(1)")
plt.plot(n, column("hash_missing_ns"), "s--", color="#2E74B5", alpha=0.55, label="Hash table – ID not present")

plt.xscale("log")
plt.yscale("log")
plt.xticks(n, [f"{x:,}" for x in n])
plt.xlabel("Number of records (n)")
plt.ylabel("Average time per search (ns)")
plt.grid(True, alpha=0.3)
plt.legend(frameon=False, fontsize=8.5)
plt.tight_layout()
plt.savefig(CHART_FILE)
print(f"Chart saved to {CHART_FILE}")