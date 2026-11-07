"""
STEP 2 - hash_table.py
======================
My own Hash Table using OPEN ADDRESSING with LINEAR PROBING.

HOW IT WORKS (simple version)
-----------------------------
1. The table is one Python list of fixed size, e.g. 31 slots:  [None, None, ..., None]
2. To store a key, compute its HOME SLOT:   home = key % capacity
        e.g. 1001 % 31 = 9   -> try slot 9 first
3. If slot 9 is already used by another key (a COLLISION),
   try the NEXT slot: 10, then 11, ... (wrap to 0 after the last slot).
   Checking the next slot one by one is called LINEAR PROBING.
4. Searching follows exactly the same path until it finds the key,
   or reaches an EMPTY slot (then the key is not in the table).

EACH SLOT CAN HOLD ONE OF THREE THINGS
--------------------------------------
    None           -> EMPTY, never used
    DELETED        -> a record was deleted here (called a "tombstone")
    HashEntry      -> USED, holds (key, value)

This class is REUSABLE: the key must be a whole number (an ID), but the
value can be anything - a Product, a Customer, a Course... so the same
class can be used in other programs.
"""


class HashEntry:

    def __init__(self, key, value):
        self.key = key        # e.g. 1001 (the product ID)
        self.value = value    # e.g. the Product object

DELETED = object()


def is_prime(n):
    """Return True if n is a prime number (used to choose the table size)."""
    if n < 2:
        return False
    i = 2
    while i * i <= n:          # only need to test divisors up to sqrt(n)
        if n % i == 0:
            return False
        i += 1
    return True

def next_prime(n):
    """Smallest prime number >= n.  e.g. next_prime(62) = 67"""
    while not is_prime(n):
        n += 1
    return n


class HashTable:

    MAX_LOAD_FACTOR = 0.7

    def __init__(self, capacity=31):

        self.capacity = next_prime(capacity)
        # The slots/buckets: one list, every slot starts EMPTY (None)
        self.slots = [None] * self.capacity
        self.size = 0          # how many records are stored
        self.deleted_count = 0  # how many slots are DELETED tombstones


    # Hash function
    def hash_function(self, key):
        return key % self.capacity

    def probe_path(self, key):

        steps = []
        index = self.hash_function(key)
        for _ in range(self.capacity):
            slot = self.slots[index]
            if slot is None:
                steps.append((index, "EMPTY - key is not in the table"))
                break
            if slot is DELETED:
                steps.append((index, "DELETED (tombstone) - keep probing"))
            elif slot.key == key:
                steps.append((index, "FOUND"))
                break
            else:
                steps.append((index, f"used by {slot.key} - collision, try next slot"))
            index = (index + 1) % self.capacity
        return steps

    # INSERT
    def insert(self, key, value):
        # Grow first if adding one more record would make the table too full
        if (self.size + self.deleted_count + 1) / self.capacity > self.MAX_LOAD_FACTOR:
            self.resize()

        index = self.hash_function(key)   # start at the home slot
        first_free = None                 # first DELETED/EMPTY slot we can use

        # Linear probing: look at up to 'capacity' slots
        for _ in range(self.capacity):
            slot = self.slots[index]

            if slot is None:
                # EMPTY slot -> the key cannot be further along, stop searching
                if first_free is None:
                    first_free = index
                break

            if slot is DELETED:
                # Can reuse this slot, but keep checking in case the key
                # already exists further along (to avoid duplicates)
                if first_free is None:
                    first_free = index
            elif slot.key == key:
                raise KeyError(f"Key {key} already exists")

            index = (index + 1) % self.capacity    # LINEAR PROBING: next slot (wraps to 0)

        # Put the record into the free slot we found
        if self.slots[first_free] is DELETED:
            self.deleted_count -= 1               # we are reusing a tombstone
        self.slots[first_free] = HashEntry(key, value)
        self.size += 1
        return first_free


    # SEARCH
    def find_slot(self, key):
        """Return (slot index, number of probes). Index is None if not found."""
        index = self.hash_function(key)
        for probes in range(1, self.capacity + 1):
            slot = self.slots[index]
            if slot is None:
                return None, probes                # reached EMPTY -> not found
            if slot is not DELETED and slot.key == key:
                return index, probes               # FOUND
            index = (index + 1) % self.capacity    # collision or tombstone -> next slot
        return None, self.capacity                 # checked every slot

    def search(self, key):
        """Return the value stored for key, or None if not found."""
        index, _ = self.find_slot(key)
        if index is None:
            return None
        return self.slots[index].value

    # UPDATE and DELETE
    def update(self, key, value):
        """Replace the value of an existing key. Returns True if done."""
        index, _ = self.find_slot(key)
        if index is None:
            return False
        self.slots[index].value = value
        return True

    def delete(self, key):

        index, _ = self.find_slot(key)
        if index is None:
            return None
        value = self.slots[index].value
        self.slots[index] = DELETED
        self.size -= 1
        self.deleted_count += 1
        return value

    # RESIZE (rehashing)
    def resize(self):

        old_slots = self.slots
        self.capacity = next_prime(self.capacity * 2)
        self.slots = [None] * self.capacity
        self.size = 0
        self.deleted_count = 0
        for slot in old_slots:
            if slot is not None and slot is not DELETED:
                self.insert(slot.key, slot.value)

    # Helpers
    def load_factor(self):
        """How full the table is: 0.0 = empty, 1.0 = full."""
        return self.size / self.capacity

    def items(self):
        """List of (key, value) for every stored record."""
        return [(s.key, s.value) for s in self.slots
                if s is not None and s is not DELETED]

    def __contains__(self, key):
        """Lets us write:  if 1001 in table: ..."""
        index, _ = self.find_slot(key)
        return index is not None

    def __len__(self):
        """Lets us write:  len(table)"""
        return self.size


# Quick test - run this file directly to see collisions and tombstones
if __name__ == "__main__":
    table = HashTable(31)
    print("Capacity:", table.capacity)

    for k in (1001, 1032, 1063, 1005):            # first three all have home slot 9
        slot = table.insert(k, f"product {k}")
        print(f"insert {k}: home slot {table.hash_function(k)} -> stored in slot {slot}")

    print("search 1063 ->", table.search(1063), "| slot, probes =", table.find_slot(1063))
    table.delete(1032)                             # slot 10 becomes DELETED
    print("after deleting 1032, search 1063 ->", table.search(1063))  # still found
    print("search 9999 ->", table.search(9999))    # not found -> None
    print("records:", len(table), "| load factor:", round(table.load_factor(), 2))

    print("probing path for 1063:")
    for slot_index, what in table.probe_path(1063):
        print(f"   slot [{slot_index}] {what}")