"""
STEP 3 - array_store.py
=======================
A ONE-DIMENSIONAL ARRAY used only to COMPARE with the hash table.

Records are kept in the order they were inserted:
    keys   = [1001, 1032, 1063, ...]
    values = [Product, Product, Product, ...]   (same positions)

To find a key we use LINEAR SEARCH: check index 0, 1, 2, ... until it matches.
    - best case : the key is at index 0       -> 1 comparison
    - worst case: the key is last / missing   -> n comparisons   => O(n)
"""


class ArrayStore:
    def __init__(self):
        self.keys = []      # the one-dimensional array of keys
        self.values = []    # the values, at the same index as their key

    def insert(self, key, value):
        """Add the record at the END of the array. Returns its index."""
        self.keys.append(key)
        self.values.append(value)
        return len(self.keys) - 1

    def find_index(self, key):
        """LINEAR SEARCH. Returns (index, comparisons). Index is None if not found."""
        for i in range(len(self.keys)):
            if self.keys[i] == key:
                return i, i + 1              # found after i+1 comparisons
        return None, len(self.keys)          # compared every element, not found

    def search(self, key):
        """Return the value stored for key, or None if not found."""
        index, _ = self.find_index(key)
        if index is None:
            return None
        return self.values[index]

    def update(self, key, value):
        index, _ = self.find_index(key)
        if index is None:
            return False
        self.values[index] = value
        return True

    def delete(self, key):
        index, _ = self.find_index(key)
        if index is None:
            return None
        self.keys.pop(index)                 # remove from both lists
        return self.values.pop(index)

    def __len__(self):
        return len(self.keys)


# Quick test
if __name__ == "__main__":
    arr = ArrayStore()
    for k in (1001, 1032, 1063):
        arr.insert(k, f"product {k}")
    print("search 1063 ->", arr.search(1063), "| index, comparisons =", arr.find_index(1063))
    print("search 9999 ->", arr.search(9999), "| index, comparisons =", arr.find_index(9999))
