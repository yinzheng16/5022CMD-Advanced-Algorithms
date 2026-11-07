"""
STEP 1 - product.py
===================
The ENTITY class: it describes ONE product sold by the pharmacy.

Every medicine in the shop becomes one Product object, for example:
    Product(1001, "Paracetamol", "500mg", "Pain Relief", 5.90, 120, False, date(2028, 3, 31))

The hash table (Step 2) does not care what a Product looks like -
it just stores it using product_id as the KEY.
"""

from datetime import date   # date is Python's built-in type for calendar dates

DATE_FORMAT = "%d-%m-%Y"

# A product with fewer units than this is shown as "Low stock" (see stock_status)
LOW_STOCK_LIMIT = 20


class Product:
    """One pharmacy product (e.g. a medicine)."""

    def __init__(self, product_id, name, strength, category, price,
                 stock_quantity, prescription_required, expiry_date):
        # int  - unique ID, used as the KEY of the hash table
        self.product_id = product_id

        # str  - medicine name only, e.g. "Paracetamol"
        self.name = name

        # str  - dosage strength, e.g. "500mg", "15mg/5ml", "0.2%"
        self.strength = strength

        # str  - group of medicine, e.g. "Pain Relief", "Antibiotic"
        self.category = category

        # float - selling price in RM, e.g. 5.90
        self.price = price

        # int  - how many units are in the shop (cannot be 3.5 boxes, so int)
        self.stock_quantity = stock_quantity

        # bool - True = customer must show a doctor's prescription (e.g. antibiotics)
        self.prescription_required = prescription_required

        # date - real date type, so we can compare dates (see is_expired below)
        self.expiry_date = expiry_date

    def full_name(self):
        """Name + strength together, e.g. "Paracetamol 500mg"."""
        return f"{self.name} {self.strength}"

    def is_expired(self):
        """Return True if the product's expiry date has already passed."""
        return self.expiry_date < date.today()

    def expiry_text(self):
        """Expiry date shown as DD-MM-YYYY, e.g. 31-03-2028.
        (Python stores dates the same way inside; only the DISPLAY format changes.)"""
        return self.expiry_date.strftime(DATE_FORMAT)   # date -> text

    def stock_status(self):

        if self.is_expired():
            return "Expired"
        if self.stock_quantity == 0:
            return "Out of stock"
        if self.stock_quantity < LOW_STOCK_LIMIT:
            return "Low stock"
        return "In stock"

    def __str__(self):
        """What print(product) shows. Python calls this automatically."""
        rx = "Yes" if self.prescription_required else "No"
        return (f"ID: {self.product_id} | Name: {self.name} | Strength: {self.strength} | "
                f"Category: {self.category}\n"
                f"Price: RM{self.price:.2f} | Stock: {self.stock_quantity} | "
                f"Prescription: {rx} | Expiry: {self.expiry_text()}")


if __name__ == "__main__":
    p = Product(1001, "Paracetamol", "500mg", "Pain Relief", 5.90, 120, False, date(2028, 3, 31))
    print(p)                                  # uses __str__
    print("Full name:", p.full_name())        # Paracetamol 500mg
    print("Expired?", p.is_expired())         # False, because 2028 is in the future
    print("Status:", p.stock_status())        # In stock (120 units, not expired)
    print("Type of price:", type(p.price))    # <class 'float'>