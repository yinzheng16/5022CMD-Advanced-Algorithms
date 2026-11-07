"""
STEP 5 - inventory_system.py   (THE MAIN PROGRAM - run this one)
=================================================================
Command-line Pharmacy Inventory System.

Every product is stored in BOTH:
    - the HashTable   (Step 2)  -> fast search
    - the ArrayStore  (Step 3)  -> slow linear search, only for comparison
so both always hold the SAME data and their search times can be compared.

The data is kept in memory (RAM) while the program runs. When the program
ends it is gone, and the pre-defined records are loaded again next time.

Menu: 1 Insert | 2 Search | 3 Edit | 4 Delete | 5 Display all | 6 View slots | 7 Exit
To add a new menu option: write a function, then add one line to the `menu` dictionary in main().
The boxes and tables are drawn by display.py.
"""

import time
from datetime import datetime

from array_store import ArrayStore
from display import SEPARATOR, pause, print_box, print_table, print_title
from hash_table import HashTable, DELETED
from product import Product, DATE_FORMAT
from sample_data import PREDEFINED_PRODUCTS


TIMING_REPEATS = 1000

INITIAL_CAPACITY = 31



# The local storage system: one hash table + one array with the same data
class PharmacyInventory:
    def __init__(self):
        self.table = HashTable(INITIAL_CAPACITY)
        self.array = ArrayStore()

    def add(self, product):
        """Insert into BOTH structures. Returns the hash table slot used."""
        slot = self.table.insert(product.product_id, product)  # KeyError if duplicate
        self.array.insert(product.product_id, product)
        return slot

    def find(self, product_id):
        return self.table.search(product_id)

    def edit(self, product):
        self.table.update(product.product_id, product)
        self.array.update(product.product_id, product)

    def remove(self, product_id):
        self.array.delete(product_id)
        return self.table.delete(product_id)


def average_search_time_ns(store, key):
    """Average time (nanoseconds) of ONE store.search(key), over TIMING_REPEATS searches.
    Works for both HashTable and ArrayStore because both have a search() method."""
    start = time.perf_counter_ns()                 # high-resolution clock, in ns
    for _ in range(TIMING_REPEATS):
        store.search(key)
    end = time.perf_counter_ns()
    return (end - start) / TIMING_REPEATS



# Input helpers - keep asking until the user types something valid,
# so a wrong input never crashes the program
def ask_int(prompt, minimum=0):
    while True:
        try:
            value = int(input(prompt))
            if value >= minimum:
                return value
            print(f"  Please enter a number >= {minimum}.")
        except ValueError:                        # e.g. user typed "abc"
            print("  Invalid number, please try again.")


def ask_price(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value >= 0:
                return round(value, 2)            # keep 2 decimal places
            print("  Price cannot be negative.")
        except ValueError:
            print("  Invalid price, please try again.")


def ask_text(prompt):
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("  This field cannot be empty.")


def ask_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()    # .lower() -> "Y" becomes "y"
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please answer y or n.")


def parse_date(text):
    return datetime.strptime(text.strip(), DATE_FORMAT).date()     # text -> date


def ask_date(prompt):
    while True:
        try:
            return parse_date(input(prompt))
        except ValueError:
            print("  Please use the format DD-MM-YYYY, e.g. 31-12-2028.")


# Lines for the boxes (each function returns a list of text lines)
def product_lines(product):
    """All details of one product, as labelled lines."""
    rx = "Required" if product.prescription_required else "Not required"
    return [
        f"{'Product ID':<14}: {product.product_id}",
        f"{'Name':<14}: {product.name}",
        f"{'Strength':<14}: {product.strength}",
        f"{'Category':<14}: {product.category}",
        f"{'Price':<14}: RM {product.price:.2f}",
        f"{'Stock':<14}: {product.stock_quantity} units",
        f"{'Prescription':<14}: {rx}",
        f"{'Expiry Date':<14}: {product.expiry_text()}",
        f"{'Status':<14}: {product.stock_status()}",
    ]


def probe_lines(table, key, found_text="FOUND"):
    """The linear probing steps for a key, as lines."""
    lines = [f"Home slot = {key} % {table.capacity} = {table.hash_function(key)}"]
    for number, (slot_index, what) in enumerate(table.probe_path(key), start=1):
        if what == "FOUND":
            what = found_text
        lines.append(f"  Probe {number}: slot [{slot_index}] -> {what}")
    return lines


def table_info_line(table):
    return (f"Table size: {table.capacity} slots | Records: {len(table)} | "
            f"Load factor: {table.load_factor():.2f}")


# Menu options
def insert_product(inv):
    """Option 1 - INSERT (required by the brief)."""
    print_title("INSERT NEW PRODUCT")
    product_id = ask_int("Enter Product ID: ", minimum=1)
    if product_id in inv.table:                      # uses HashTable.__contains__
        print(f"\nProduct ID {product_id} already exists. Use Edit instead.")
        return

    product = Product(
        product_id,
        ask_text("Enter Product Name (e.g. Paracetamol): "),
        ask_text("Enter Strength (e.g. 500mg): "),
        ask_text("Enter Category: "),
        ask_price("Enter Price (RM): "),
        ask_int("Enter Stock Quantity: "),
        ask_yes_no("Prescription required? (y/n): "),
        ask_date("Enter Expiry Date (DD-MM-YYYY): "),
    )
    old_capacity = inv.table.capacity
    slot = inv.add(product)

    lines = product_lines(product) + [SEPARATOR, f"Stored in slot [{slot}]", "Linear probing process:"]
    lines += probe_lines(inv.table, product_id, found_text="free slot - product STORED here")
    if inv.table.capacity != old_capacity:
        lines.append(f"(Table was over {HashTable.MAX_LOAD_FACTOR:.0%} full -> "
                     f"resized from {old_capacity} to {inv.table.capacity} slots)")
    lines += [SEPARATOR, table_info_line(inv.table)]
    print()
    print_box("PRODUCT INSERTED SUCCESSFULLY", lines)


def search_product(inv):
    """Option 2 - SEARCH (required by the brief). Also times hash table vs array."""
    print_title("SEARCH PRODUCT")
    product_id = ask_int("Enter Product ID to search: ", minimum=1)
    product = inv.find(product_id)
    _, probes = inv.table.find_slot(product_id)
    _, comparisons = inv.array.find_index(product_id)

    # Time the SAME search in both structures
    hash_ns = average_search_time_ns(inv.table, product_id)
    array_ns = average_search_time_ns(inv.array, product_id)
    if hash_ns < array_ns:
        verdict = f"-> Hash table was {array_ns / hash_ns:.1f}x faster"
    else:
        verdict = f"-> Array was {hash_ns / array_ns:.1f}x faster (only {len(inv.array)} records)"

    lines = product_lines(product) + [SEPARATOR] if product else []
    lines += ["How the hash table searched (linear probing):"]
    lines += probe_lines(inv.table, product_id)
    lines += [SEPARATOR,
              f"Search time (average of {TIMING_REPEATS} searches):",
              f"  Hash Table : {hash_ns:>10,.1f} ns   ({probes} probe(s))",
              f"  Array      : {array_ns:>10,.1f} ns   ({comparisons} comparison(s))",
              f"  {verdict}"]
    print()
    print_box("PRODUCT FOUND" if product else f"PRODUCT {product_id} NOT FOUND", lines)


def edit_product(inv):
    """Option 3 - EDIT (optional). Every field except the ID can be changed.
    Press Enter to keep the old value. (The ID is the hash table KEY, so
    changing it would mean deleting and inserting the product again.)"""
    print_title("EDIT PRODUCT")
    product_id = ask_int("Enter Product ID to edit: ", minimum=1)
    product = inv.find(product_id)
    if product is None:
        print("\nProduct not found.")
        return

    print()
    print_box("CURRENT DETAILS", product_lines(product))
    print("Press Enter to keep the current value.")
    name = input(f"Name [{product.name}]: ").strip()
    strength = input(f"Strength [{product.strength}]: ").strip()
    category = input(f"Category [{product.category}]: ").strip()
    price = input(f"Price [{product.price:.2f}]: ").strip()
    stock = input(f"Stock [{product.stock_quantity}]: ").strip()
    rx = input(f"Prescription required (y/n) [{'y' if product.prescription_required else 'n'}]: ").strip().lower()
    expiry = input(f"Expiry date DD-MM-YYYY [{product.expiry_text()}]: ").strip()

    if not any([name, strength, category, price, stock, rx, expiry]):
        print("\nNo changes made.")
        return

    # Convert and check ALL inputs first; only change the product if everything is valid
    try:
        new_price = round(float(price), 2) if price else product.price
        new_stock = int(stock) if stock else product.stock_quantity
        new_expiry = parse_date(expiry) if expiry else product.expiry_date
        if new_price < 0 or new_stock < 0:
            raise ValueError
        if rx not in ("", "y", "yes", "n", "no"):
            raise ValueError
    except ValueError:
        print("\nInvalid value entered - no changes saved.")
        return

    product.name = name or product.name                 # "or": keep old value if empty
    product.strength = strength or product.strength
    product.category = category or product.category
    product.price = new_price
    product.stock_quantity = new_stock
    if rx:
        product.prescription_required = rx in ("y", "yes")
    product.expiry_date = new_expiry

    inv.edit(product)
    print()
    print_box("PRODUCT UPDATED", product_lines(product))


def delete_product(inv):
    """Option 4 - DELETE (optional). Asks for confirmation first.
    The slot becomes a DELETED tombstone."""
    print_title("DELETE PRODUCT")
    product_id = ask_int("Enter Product ID to delete: ", minimum=1)
    product = inv.find(product_id)
    if product is None:
        print("\nProduct not found.")
        return

    print()
    print_box("PRODUCT TO DELETE", product_lines(product))
    if not ask_yes_no(f"Are you sure you want to delete {product.full_name()}? (y/n): "):
        print("\nDelete cancelled.")
        return

    slot, _ = inv.table.find_slot(product_id)
    inv.remove(product_id)
    print(f"\nDeleted: {product.full_name()} - slot [{slot}] is now marked as DELETED")


def display_all(inv):
    """Option 5 - list every product in a table, sorted by ID."""
    products = sorted((p for _, p in inv.table.items()), key=lambda p: p.product_id)
    rows = []
    for p in products:
        rows.append([p.product_id, p.name, p.strength, p.category, f"{p.price:.2f}",
                     p.stock_quantity, "Yes" if p.prescription_required else "No",
                     p.expiry_text(), p.stock_status()])

    print_title(f"ALL PRODUCTS ({len(products)})")
    print_table(["ID", "Name", "Strength", "Category", "Price (RM)", "Stock",
                 "Rx", "Expiry", "Status"],
                rows, right_align=(0, 4, 5))         # numbers aligned to the right

    # short summary under the table
    statuses = [p.stock_status() for p in products]
    print(f"Total: {len(products)} | In stock: {statuses.count('In stock')} | "
          f"Low stock: {statuses.count('Low stock')} | "
          f"Out of stock: {statuses.count('Out of stock')} | Expired: {statuses.count('Expired')}")


def view_slots(inv):
    """Option 6 - show every slot of the hash table (to see linear probing).
    Runs of empty slots are joined into one row so the table stays short."""
    t = inv.table
    rows = []
    index = 0
    while index < t.capacity:
        slot = t.slots[index]
        if slot is None:
            # join consecutive EMPTY slots into one row, e.g. "3-7"
            start = index
            while index + 1 < t.capacity and t.slots[index + 1] is None:
                index += 1
            label = str(start) if start == index else f"{start}-{index}"
            rows.append([label, "EMPTY", "", "", "", ""])
        elif slot is DELETED:
            rows.append([index, "DELETED", "", "(tombstone)", "", "search keeps probing"])
        else:
            home = t.hash_function(slot.key)
            moved = (index - home) % t.capacity       # how many slots after its home slot
            note = "at home slot" if moved == 0 else f"moved {moved} slot(s) by probing"
            rows.append([index, "USED", slot.key, slot.value.full_name(), home, note])
        index += 1

    print_title("HASH TABLE SLOTS")
    print(table_info_line(t))
    print_table(["Slot", "State", "Key", "Product", "Home", "Linear probing"],
                rows, right_align=(0, 2, 4))



# Main program
def main():
    inventory = PharmacyInventory()
    for product in PREDEFINED_PRODUCTS:              # load the pre-defined records
        inventory.add(product)
    print(f"{len(PREDEFINED_PRODUCTS)} pre-defined products loaded.")

    # menu number -> (text shown, function to call)
    menu = {
        "1": ("Insert Product", insert_product),
        "2": ("Search Product", search_product),
        "3": ("Edit Product", edit_product),
        "4": ("Delete Product", delete_product),
        "5": ("Display All Products", display_all),
        "6": ("View Hash Table Slots", view_slots),
    }
    exit_option = str(len(menu) + 1)                 # "7" - always the number after the last option

    while True:
        print("\n==== Pharmacy Inventory System ====")
        for number, (text, _) in menu.items():
            print(f"{number}. {text}")
        print(f"{exit_option}. Exit")

        choice = ""
        while choice == "":
            choice = input("Enter choice: ").strip()

        if choice == exit_option:
            print("\nExiting Inventory System. Goodbye!")
            break
        elif choice in menu:
            print()
            menu[choice][1](inventory)               # call the chosen function
            pause()
        else:
            print(f"Invalid choice, please enter 1-{exit_option}.")


if __name__ == "__main__":
    main()