"""
STEP 5 - graph_view.py
======================
Ways to SEE the course graph:

1. tree_lines()          - a tree in the console, e.g. every prerequisite of CS301:
                               CS301 Advanced Algorithms
                               ├── CS201 Data Structures
                               │   ├── CS101 Introduction to Programming
                               │   └── CS102 Discrete Mathematics
                               └── CS102 Discrete Mathematics
2. save_graph_picture()  - draws the whole graph as a PNG picture with matplotlib,
                           one column per YEAR of study (Year 1, Year 2, Year 3).
"""

import os

# colours used in the picture
CORE_COLOUR = "#DCE6F4"        # light blue box
CORE_EDGE = "#2F5597"          # dark blue border
ELECTIVE_COLOUR = "#FDE9D9"    # light orange box
ELECTIVE_EDGE = "#C55A11"      # dark orange border


def tree_lines(start, children, label):
    """Build the lines of a tree drawing, starting from `start`.

    children(x) -> the list of items below x (e.g. the prerequisites of x)
    label(x)    -> the text to show for x
    Works by RECURSION: each child draws its own smaller tree under it.
    """
    lines = [label(start)]

    def add(node, prefix):
        kids = children(node)
        for i, kid in enumerate(kids):
            last = (i == len(kids) - 1)
            lines.append(prefix + ("└── " if last else "├── ") + label(kid))
            add(kid, prefix + ("    " if last else "│   "))   # go one level deeper

    add(start, "")
    return lines


def layout(columns, incoming, first_key=lambda course: 0):

    place = {}
    for col, column in enumerate(columns):
        def average_row(course):
            rows = [place[p][1] for p in incoming(course) if p in place]
            return sum(rows) / len(rows) if rows else 0
        ordered = sorted(column, key=lambda c: (first_key(c), average_row(c), c.course_code))
        for row, course in enumerate(ordered):
            place[course] = (col, row)
    return place


def save_graph_picture(system, filename="course_graph.png"):
    """Draw every course and prerequisite link and save it as a PNG file.
    One column per year of study. Returns (True, path) or (False, reason)."""
    try:
        import matplotlib
        matplotlib.use("Agg")                      # draw to a file, no window needed
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch
    except ImportError:
        return False, "matplotlib is not installed (File > Settings > Python Interpreter > + > matplotlib)."

    levels = system.study_plan()          # Kahn's algorithm: prerequisites always come first
    if levels is None:
        return False, "The graph has a cycle, so it cannot be drawn."

    # 1) Columns = years. Inside a year, courses are listed in study-plan order,
    #    (Kahn's algorithm order), so if one course of a year needs another course
    #    of the SAME year, the prerequisite is placed above it.
    order = {course: number for number, level in enumerate(levels) for course in level}
    years = sorted({c.year for c in system.courses()})
    columns = [sorted([c for c in system.courses() if c.year == y], key=lambda c: (order[c], c.course_code))
               for y in years]

    box_w, box_h, gap_x, gap_y = 2.6, 0.9, 1.6, 0.5
    tallest = max(len(column) for column in columns)
    place = layout(columns, system.prerequisites_of, first_key=lambda c: order[c])
    pos = {}
    for course, (col, row) in place.items():
        centre_shift = (tallest - len(columns[col])) * (box_h + gap_y) / 2   # centre short columns
        pos[course] = (col * (box_w + gap_x), -(centre_shift + row * (box_h + gap_y)))
    bottom = min(y for _, y in pos.values())          # y of the lowest box

    width = len(columns) * (box_w + gap_x) - gap_x
    fig, ax = plt.subplots(figsize=(width * 0.9, (tallest * (box_h + gap_y) + 2.2) * 0.9), dpi=150)
    line = dict(color="#555555", lw=1.2, zorder=1)
    arrow = dict(arrowstyle="-|>", color="#555555", lw=1.2, shrinkA=0, shrinkB=1)

    # 2) Arrows
    #    - to the NEXT year: a straight line
    #    - skipping a year : down into a "lane" below the boxes, so it never crosses a box
    #    - inside the SAME year (or to an earlier year): a curve on the right of the boxes
    lane = 0
    for course in system.courses():
        for target in system.unlocked_by(course):
            step = place[target][0] - place[course][0]          # how many columns to the right
            if step == 1:
                x1, y1 = pos[course][0] + box_w, pos[course][1] + box_h / 2
                x2, y2 = pos[target][0], pos[target][1] + box_h / 2
                ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=arrow, zorder=1)
            elif step > 1:
                lane += 1
                ly = bottom - 0.35 * lane                       # this arrow's own lane
                x1, y1 = pos[course][0] + box_w, pos[course][1] + box_h / 2
                x2, y2 = pos[target][0], pos[target][1] + box_h / 2
                ax.plot([x1, x1 + gap_x * 0.45, x2 - gap_x * 0.45], [y1, ly, ly], **line)
                ax.annotate("", xy=(x2, y2), xytext=(x2 - gap_x * 0.45, ly), arrowprops=arrow, zorder=1)
            else:
                x1, y1 = pos[course][0] + box_w, pos[course][1] + box_h / 2
                x2, y2 = pos[target][0] + box_w, pos[target][1] + box_h / 2
                bend = -0.6 if y2 < y1 else 0.6                            # always bulge to the RIGHT
                curved = dict(arrow, connectionstyle=f"arc3,rad={bend}")
                ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=curved, zorder=1)

    # 3) One rounded box per course (drawn on top of the arrows)
    for course, (x, y) in pos.items():
        face = CORE_COLOUR if course.is_core() else ELECTIVE_COLOUR
        edge = CORE_EDGE if course.is_core() else ELECTIVE_EDGE
        ax.add_patch(FancyBboxPatch((x, y), box_w, box_h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                    facecolor=face, edgecolor=edge, linewidth=1.6, zorder=3))
        ax.text(x + box_w / 2, y + box_h * 0.64, course.course_code, ha="center", va="center",
                fontsize=11, fontweight="bold", color="#222222", zorder=4)
        ax.text(x + box_w / 2, y + box_h * 0.30, course.course_name, ha="center", va="center",
                fontsize=8, color="#333333", zorder=4)

    # 4) Year titles and legend
    for col, year in enumerate(years):
        ax.text(col * (box_w + gap_x) + box_w / 2, box_h + 0.5, f"Year {year}",
                ha="center", fontsize=12, fontweight="bold", color="#444444")
    legend_y = bottom - 0.35 * lane - 0.8
    for i, (name, face, edge) in enumerate([("Core", CORE_COLOUR, CORE_EDGE),
                                            ("Elective", ELECTIVE_COLOUR, ELECTIVE_EDGE)]):
        ax.add_patch(FancyBboxPatch((i * 1.6, legend_y), 0.3, 0.25, boxstyle="round,pad=0.02",
                                    facecolor=face, edgecolor=edge))
        ax.text(i * 1.6 + 0.45, legend_y + 0.12, name, va="center", fontsize=9)
    ax.text(3.4, legend_y + 0.12, "Arrow: prerequisite  \u2192  course it unlocks", va="center", fontsize=9)

    ax.set_xlim(-0.3, width + 1.0)
    ax.set_ylim(legend_y - 0.4, box_h + 1.0)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
    return True, os.path.abspath(filename)


def open_file(path):
    """Open the picture with the computer's default image viewer (Windows only)."""
    if hasattr(os, "startfile"):
        os.startfile(path)


# Quick test
if __name__ == "__main__":
    from course_system import build_initial_system
    s = build_initial_system()
    cs301 = s.get("CS301")
    for line in tree_lines(cs301, s.prerequisites_of, lambda c: f"{c.course_code} {c.course_name}"):
        print(line)
    print(save_graph_picture(s, "course_graph_test.png"))