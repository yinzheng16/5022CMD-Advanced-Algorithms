"""
display.py  (helper for STEP 5)
===============================
Functions that only DRAW things on the screen: boxes, tables and the
"Press Enter to continue" pause. Keeping them here keeps inventory_system.py short,
and they can be reused by other programs (e.g. Question 2).

Box-drawing characters used:   ╔ ═ ╗ ║ ╠ ╣ ╚ ╝   and   ┌ ─ ┬ ┐ │ ├ ┼ ┤ └ ┴ ┘
"""

MIN_BOX_WIDTH = 60     # a box is at least this wide (it grows for long lines)


# ---------------------------------------------------------------------------
# Box:  a title + lines, with "---" lines turned into separators
# ---------------------------------------------------------------------------
SEPARATOR = "---"      # put this in the list of lines to draw a divider


def print_box(title, lines):
    """Draw a double-line box, for example:

        ╔══════════════════════╗
        ║    PRODUCT FOUND     ║
        ╠══════════════════════╣
        ║  Product ID : 1063   ║
        ╟──────────────────────╢     <- SEPARATOR
        ║  ...                 ║
        ╚══════════════════════╝
    The width is calculated from the longest line, so nothing is cut off.
    """
    width = max([MIN_BOX_WIDTH, len(title) + 4] + [len(line) + 4 for line in lines])
    inner = width - 2                                  # space between ║ and ║

    print("╔" + "═" * inner + "╗")
    print("║" + title.center(inner) + "║")
    print("╠" + "═" * inner + "╣")
    for line in lines:
        if line == SEPARATOR:
            print("╟" + "─" * inner + "╢")
        else:
            print("║ " + line.ljust(inner - 1) + "║")    # ljust pads with spaces
    print("╚" + "═" * inner + "╝")


def print_title(title):
    """A small heading box with only a title, e.g. at the start of Insert:
        ╔══════════════════════╗
        ║  INSERT NEW PRODUCT  ║
        ╚══════════════════════╝
    """
    inner = max(MIN_BOX_WIDTH, len(title) + 4) - 2
    print("╔" + "═" * inner + "╗")
    print("║" + title.center(inner) + "║")
    print("╚" + "═" * inner + "╝")


# ---------------------------------------------------------------------------
# Table:  headers + rows, column widths calculated automatically
# ---------------------------------------------------------------------------
def print_table(headers, rows, right_align=()):
    """Draw a table with borders, for example:

        ┌──────┬─────────────┐
        │ ID   │ Name        │
        ├──────┼─────────────┤
        │ 1001 │ Paracetamol │
        └──────┴─────────────┘
    headers     : list of column titles
    rows        : list of rows, each row is a list of values
    right_align : column numbers to align right (numbers look better that way)
    """
    text_rows = [[str(value) for value in row] for row in rows]
    # each column is as wide as its longest value (header included)
    widths = [len(h) for h in headers]
    for row in text_rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    def border(left, middle, right):
        return left + middle.join("─" * (w + 2) for w in widths) + right

    def format_row(values):
        cells = []
        for i, value in enumerate(values):
            if i in right_align:
                cells.append(" " + value.rjust(widths[i]) + " ")
            else:
                cells.append(" " + value.ljust(widths[i]) + " ")
        return "│" + "│".join(cells) + "│"

    print(border("┌", "┬", "┐"))
    print(format_row(headers))
    print(border("├", "┼", "┤"))
    for row in text_rows:
        print(format_row(row))
    print(border("└", "┴", "┘"))


# ---------------------------------------------------------------------------
# Pause:  "Press Enter to continue..."
# ---------------------------------------------------------------------------
def pause():
    """Wait for Enter, so the user can read the result before the menu appears again."""
    input("\nPress Enter to continue...")