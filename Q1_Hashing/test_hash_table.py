"""
test_hash_table.py  -  automatic tests for the HashTable (Step 2)
================================================================
Run it like any other file (right-click -> Run). Each test checks one rule
of the hash table. "OK" at the end means every test passed.

unittest is Python's built-in testing library (nothing to install).
Every method whose name starts with test_ is run automatically.
"""

import random
import unittest

from hash_table import HashTable, DELETED


class TestHashTable(unittest.TestCase):

    def __str__(self):
        """Show only the test name in the output, e.g. "test_home_slot"."""
        return self._testMethodName

    def setUp(self):
        """Runs before EVERY test: a fresh table of 31 slots."""
        self.table = HashTable(31)

    def test_home_slot(self):
        # home slot = key % capacity
        self.assertEqual(self.table.hash_function(1001), 9)       # 1001 % 31 = 9
        self.assertEqual(self.table.hash_function(31), 0)

    def test_insert_and_search(self):
        slot = self.table.insert(1005, "Cetirizine")
        self.assertEqual(slot, 13)                                 # 1005 % 31 = 13, no collision
        self.assertEqual(self.table.search(1005), "Cetirizine")

    def test_collision_uses_linear_probing(self):
        # 1001, 1032 and 1063 all have home slot 9 -> slots 9, 10, 11
        self.assertEqual(self.table.insert(1001, "A"), 9)
        self.assertEqual(self.table.insert(1032, "B"), 10)
        self.assertEqual(self.table.insert(1063, "C"), 11)
        self.assertEqual(self.table.find_slot(1063), (11, 3))      # found after 3 probes

    def test_wrap_around_to_slot_0(self):
        # slot 30 is the last slot; the next probe must wrap to slot 0
        self.table.insert(30, "A")                                 # 30 % 31 = 30
        self.assertEqual(self.table.insert(61, "B"), 0)            # 61 % 31 = 30 -> taken -> slot 0

    def test_search_missing_key(self):
        self.table.insert(1001, "A")
        self.assertIsNone(self.table.search(9999))

    def test_duplicate_key_rejected(self):
        self.table.insert(1001, "A")
        with self.assertRaises(KeyError):
            self.table.insert(1001, "again")

    def test_update(self):
        self.table.insert(1001, "old")
        self.assertTrue(self.table.update(1001, "new"))
        self.assertEqual(self.table.search(1001), "new")
        self.assertFalse(self.table.update(9999, "x"))             # key not in table

    def test_delete_leaves_tombstone_and_keeps_chain(self):
        for key in (1001, 1032, 1063):
            self.table.insert(key, key)
        self.table.delete(1032)
        self.assertIs(self.table.slots[10], DELETED)               # tombstone in slot 10
        self.assertEqual(self.table.search(1063), 1063)            # still found past the tombstone
        self.assertIsNone(self.table.search(1032))
        self.assertEqual(len(self.table), 2)

    def test_insert_reuses_tombstone(self):
        self.table.insert(27, "A")                                 # 27 % 31 = 27
        self.table.delete(27)
        self.assertEqual(self.table.insert(58, "B"), 27)           # 58 % 31 = 27 -> reuses slot 27
        self.assertEqual(self.table.deleted_count, 0)

    def test_resize_when_load_factor_exceeds_limit(self):
        # 31 * 0.7 = 21.7, so the 22nd insert makes the table grow to 67 slots
        for key in range(21):
            self.table.insert(key, key)
        self.assertEqual(self.table.capacity, 31)
        self.table.insert(21, 21)
        self.assertEqual(self.table.capacity, 67)                  # next prime >= 62
        for key in range(22):                                      # nothing lost after rehashing
            self.assertEqual(self.table.search(key), key)

    def test_random_operations_match_python_dict(self):
        # 30,000 random inserts/searches/deletes, checked against Python's own dict
        expected = {}
        rng = random.Random(1)
        for i in range(30_000):
            key = rng.randint(0, 900)
            action = rng.random()
            if action < 0.5 and key not in expected:
                self.table.insert(key, i)
                expected[key] = i
            elif action < 0.75:
                self.assertEqual(self.table.delete(key), expected.pop(key, None))
            else:
                self.assertEqual(self.table.search(key), expected.get(key))
        self.assertEqual(dict(self.table.items()), expected)
        self.assertEqual(len(self.table), len(expected))


if __name__ == "__main__":
    unittest.main(verbosity=2)        # verbosity=2 prints the name of every test