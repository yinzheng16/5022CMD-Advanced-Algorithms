"""
STEP 4 - sample_data.py
=======================
The pre-defined pharmacy records that are inserted when the system starts.

Some IDs were chosen ON PURPOSE to collide in a table of 31 slots:
    1001 % 31 = 9
    1032 % 31 = 9     <- same home slot as 1001  -> collision
    1063 % 31 = 9     <- same home slot again    -> collision
So you can SEE linear probing in the slot viewer: they end up in slots 9, 10, 11.
"""

from datetime import date
from product import Product

#        Product(ID,   Name,                     Strength,    Category,      Price,  Stock, Prescription, Expiry date)
PREDEFINED_PRODUCTS = [
    Product(1001, "Paracetamol",              "500mg",     "Pain Relief",    5.90, 120, False, date(2028, 3, 31)),
    Product(1032, "Ibuprofen",                "200mg",     "Pain Relief",    8.50,  80, False, date(2027, 11, 30)),
    Product(1063, "Amoxicillin",              "250mg",     "Antibiotic",    18.00,  40, True,  date(2027, 6, 30)),
    Product(1005, "Cetirizine",               "10mg",      "Allergy",        9.90,  65, False, date(2028, 1, 31)),
    Product(1010, "Loratadine",               "10mg",      "Allergy",       12.40,  50, False, date(2027, 9, 30)),
    Product(1017, "Omeprazole",               "20mg",      "Gastric",       15.80,  45, True,  date(2027, 12, 31)),
    Product(1020, "Vitamin C",                "1000mg",    "Supplement",    25.00, 150, False, date(2028, 5, 31)),
    Product(1024, "Metformin",                "500mg",     "Diabetes",      14.20,  60, True,  date(2027, 8, 31)),
    Product(1031, "Oral Rehydration Salts",   "20.5g",     "Digestive",      3.50, 200, False, date(2028, 2, 29)),
    Product(1042, "Dextromethorphan Syrup",   "15mg/5ml",  "Cough & Cold",  11.90,  35, False, date(2027, 4, 30)),
    Product(1050, "Amlodipine",               "5mg",       "Hypertension",  16.70,  55, True,  date(2027, 10, 31)),
    Product(1056, "Chlorhexidine Mouthwash",  "0.2%",      "Oral Care",     13.60,  25, False, date(2028, 7, 31)),
]

# Quick test
if __name__ == "__main__":
    for p in PREDEFINED_PRODUCTS:
        print(f"{p.product_id}  home slot = {p.product_id % 31:>2}   {p.full_name()}")