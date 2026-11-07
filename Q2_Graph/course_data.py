"""
STEP 3 - course_data.py
=======================
The pre-defined course profiles (8 courses: the brief asks for 5 to 10)
and their prerequisite links.

    Year 1          Year 2              Year 3
    CS101 --------> CS201 ------------> CS301 Advanced Algorithms
      |      +----> (Data Structures) -> CS302 Machine Learning (elective)
      |      |
    CS102 ---+-----------------------> CS301, CS302
      |
    CS101 --------> CS202 (OOP) ------> CS303 Mobile App Development (elective)
    CS101 --------> CS203 (Database) -> CS303

Some courses only REQUIRE others (CS303), some are only REQUIRED by others
(CS101, CS102), and some do both (CS201) - like a real registration system.
"""

from course import CORE, ELECTIVE, Course

#       Course(code,   name,                          credits, level,    year, description)
INITIAL_COURSES = [
    Course("CS101", "Introduction to Programming",     4, CORE,     1,
           "Python basics: variables, decisions, loops, functions and files."),
    Course("CS102", "Discrete Mathematics",            4, CORE,     1,
           "Logic, sets, relations, counting and proof techniques."),
    Course("CS201", "Data Structures",                 4, CORE,     2,
           "Lists, stacks, queues, trees, hash tables and their complexity."),
    Course("CS202", "Object-Oriented Programming",     4, CORE,     2,
           "Classes, inheritance, polymorphism and design principles."),
    Course("CS203", "Database Systems",                3, CORE,     2,
           "Relational model, SQL, normalisation and transactions."),
    Course("CS301", "Advanced Algorithms",             4, CORE,     3,
           "Graph algorithms, hashing, complexity theory and concurrency."),
    Course("CS302", "Machine Learning",                3, ELECTIVE, 3,
           "Supervised and unsupervised learning with practical projects."),
    Course("CS303", "Mobile App Development",          3, ELECTIVE, 3,
           "Building data-driven Android and iOS applications."),
]

# (prerequisite, course)  means an edge  prerequisite -> course
# e.g. ("CS101", "CS201"): CS101 must be passed before taking CS201
INITIAL_PREREQUISITES = [
    ("CS101", "CS201"), ("CS102", "CS201"),
    ("CS101", "CS202"), ("CS101", "CS203"),
    ("CS201", "CS301"), ("CS102", "CS301"),
    ("CS201", "CS302"), ("CS102", "CS302"),
    ("CS202", "CS303"), ("CS203", "CS303"),
]

# Quick test
if __name__ == "__main__":
    print(len(INITIAL_COURSES), "courses,", len(INITIAL_PREREQUISITES), "prerequisite links")
    for c in INITIAL_COURSES:
        print(f"  {c.course_code}  {c.course_name:<30} {c.level:<9} Year {c.year}")