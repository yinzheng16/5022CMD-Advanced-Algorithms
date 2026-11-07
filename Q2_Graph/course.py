"""
STEP 2 - course.py
==================
The ENTITY class: it describes ONE course offered by the university.

The Graph (Step 1) does not know anything about courses - it just stores
Course objects as its vertices.
"""

CORE = "Core"
ELECTIVE = "Elective"


class Course:
    """One university course, e.g. CS201 Data Structures."""

    def __init__(self, course_code, course_name, credit_hours, level, year, description):
        # str  - unique code, e.g. "CS201"; used to find the course
        self.course_code = course_code

        # str  - full name, e.g. "Data Structures"
        self.course_name = course_name

        # int  - credit hours, e.g. 4 (always a whole number)
        self.credit_hours = credit_hours

        # str  - CORE (compulsory) or ELECTIVE (optional); decides how the profile is shown
        self.level = level

        # int  - year of study in which the course is normally taken (1, 2 or 3)
        self.year = year

        # str  - one-sentence summary of what the course teaches
        self.description = description

    # Two Course objects are the SAME vertex if they have the same code.
    # __eq__ and __hash__ let a Course be used as a dictionary key, which is
    # how the Graph stores its vertices (outgoing[course], incoming[course]).
    def __eq__(self, other):
        return isinstance(other, Course) and self.course_code == other.course_code

    def __hash__(self):
        return hash(self.course_code)

    def __repr__(self):
        return self.course_code          # short form, e.g. when a list is printed

    def is_core(self):
        return self.level == CORE

    def short_label(self):
        """e.g. "CS201 (Data Structures)" """
        return f"{self.course_code} ({self.course_name})"


# Quick test
if __name__ == "__main__":
    c = Course("CS201", "Data Structures", 4, CORE, 2, "Lists, stacks, queues, trees and hash tables.")
    same = Course("CS201", "Another name", 3, ELECTIVE, 1, "-")
    print(c.short_label(), "| core?", c.is_core())
    print("Same course code -> equal?", c == same)          # True
    print("Usable as dict key:", {c: "ok"}[same])           # ok