"""
STEP 6 - main.py   (THE MAIN PROGRAM - run this one)
====================================================
Menu-driven University Course Prerequisite System.

Menu groups shown to the user: BROWSE COURSES (1-4), MANAGE COURSES (5-8),
PLAN YOUR STUDIES (9-11). How they match the brief:

Mandatory features (required by the brief)
    1. View all courses
    2. View course details (all information, level ignored)
    3. View prerequisites of a course       -> incoming edges
    4. View courses unlocked by a course    -> outgoing edges
Advanced features (optional in the brief - all four are done)
    5. Add a new course                     -> new vertex
    6. View course profile (core = all details, elective = name only)
    7. Add a prerequisite                   -> new edge Y -> X
    8. Remove a prerequisite                -> remove edge Y -> X
Extra features (my own additions)
    9.  Full prerequisite tree (direct AND indirect prerequisites)
    10. Study plan by year (Kahn's algorithm puts prerequisites first; the plan is checked)
    11. Prerequisite map of the whole graph + save it as a picture

To add a menu option: write a function, then add one line to MENU_GROUPS at the bottom.
The boxes and tables are drawn by display.py (the same file as in Question 1).
"""

from course import CORE, ELECTIVE, Course
from course_system import MAX_COURSES, build_initial_system
from display import SEPARATOR, pause, print_box, print_table, print_title
from graph_view import open_file, save_graph_picture, tree_lines

GRAPH_PICTURE = "course_graph.png"     # file name used by option 11


# Small helpers
def ask_course(system, prompt="Enter Course Code: "):
    """Ask for a course code and return the Course, or None (with a message)."""
    course = system.get(input(prompt))
    if course is None:
        codes = ", ".join(c.course_code for c in system.courses())
        print(f"  Course not found. Valid codes: {codes}")
    return course


def ask_int(prompt, minimum, maximum):
    while True:
        try:
            value = int(input(prompt))
            if minimum <= value <= maximum:
                return value
            print(f"  Please enter a number from {minimum} to {maximum}.")
        except ValueError:
            print("  Invalid number, please try again.")


def ask_text(prompt):
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("  This field cannot be empty.")


def detail_lines(course):
    """Every attribute of a course, as labelled lines for a box."""
    return [
        f"{'Course Code':<13}: {course.course_code}",
        f"{'Course Name':<13}: {course.course_name}",
        f"{'Credit Hours':<13}: {course.credit_hours}",
        f"{'Level':<13}: {course.level}",
        f"{'Year':<13}: {course.year}",
        f"{'Description':<13}: {course.description}",
    ]


def course_list_lines(courses):
    """'- CS201 (Data Structures)' for each course, or '(none)'."""
    return [f"- {c.short_label()}" for c in courses] or ["(none)"]


def label(course):
    return f"{course.course_code} {course.course_name}"



# Mandatory features
def view_all_courses(system):
    """(a) Display a list of all the courses' names."""
    rows = [[i, c.course_code, c.course_name, c.level, c.credit_hours, c.year]
            for i, c in enumerate(system.courses(), start=1)]
    print_title(f"AVAILABLE COURSES ({len(rows)})")
    print_table(["No", "Code", "Course Name", "Level", "Credits", "Year"], rows, right_align=(0, 4, 5))


def view_course_details(system):
    """(b) All information of one course, whatever its level."""
    print_title("VIEW COURSE DETAILS")
    course = ask_course(system)
    if course:
        print_box(f"COURSE DETAILS: {course.course_code}", detail_lines(course))


def view_prerequisites(system):
    """(c) Prerequisites = the INCOMING adjacent vertices of the course."""
    print_title("VIEW PREREQUISITES")
    course = ask_course(system)
    if course:
        prereqs = system.prerequisites_of(course)
        print_box(f"PREREQUISITES FOR {course.course_code} - {course.course_name}",
                  course_list_lines(prereqs) + [SEPARATOR, f"{len(prereqs)} direct prerequisite(s)"])


def view_unlocked_courses(system):
    """(d) Unlocked courses = the OUTGOING adjacent vertices of the course."""
    print_title("VIEW COURSES UNLOCKED")
    course = ask_course(system)
    if course:
        unlocked = system.unlocked_by(course)
        print_box(f"COURSES UNLOCKED BY {course.course_code} - {course.course_name}",
                  course_list_lines(unlocked) + [SEPARATOR, f"{len(unlocked)} course(s) unlocked"])



# Advanced features
def add_new_course(system):
    """(a) Add a course on demand = a new vertex in the graph."""
    print_title(f"ADD A NEW COURSE ({len(system.catalogue)}/{MAX_COURSES} courses)")
    if len(system.catalogue) >= MAX_COURSES:
        print(f"Cannot add more courses - the maximum is {MAX_COURSES}.")
        return
    code = ask_text("Enter new Course Code (e.g. CS304): ").upper()
    if system.get(code):
        print(f"\nCourse code {code} already exists.")
        return
    name = ask_text("Enter Course Name: ")
    credit_hours = ask_int("Enter Credit Hours (1-6): ", 1, 6)
    year = ask_int("Enter Year of Study (1-3): ", 1, 3)
    while True:
        answer = input("Level - (C)ore or (E)lective: ").strip().upper()
        if answer in ("C", "CORE", "E", "ELECTIVE"):
            level = CORE if answer.startswith("C") else ELECTIVE
            break
        print("  Please type C or E.")
    description = ask_text("Enter Description: ")

    course = Course(code, name, credit_hours, level, year, description)
    ok, message = system.add_course(course)
    print()
    if ok:
        print_box("COURSE ADDED", detail_lines(course) + [SEPARATOR,
                  f"Courses in the system: {len(system.catalogue)}/{MAX_COURSES}",
                  "Tip: use option 7 to give it prerequisites."])
    else:
        print(message)


def view_course_profile(system):
    """(b) Core course = all details; elective course = name only."""
    print_title("VIEW COURSE PROFILE")
    course = ask_course(system)
    if course is None:
        return
    if course.is_core():
        print_box(f"CORE COURSE PROFILE: {course.course_code}", detail_lines(course))
    else:
        print_box("ELECTIVE COURSE PROFILE", [f"{'Course Name':<13}: {course.course_name}", SEPARATOR,
                                              "Other details are hidden for elective courses."])


def add_prerequisite(system):
    """(c) Course X adds course Y as a prerequisite = new edge Y -> X.
    X = the course that needs the prerequisite, Y = the course passed before it."""
    print_title("ADD A PREREQUISITE")
    print("Example: CS303 needs CS201 first  ->  type CS303, then CS201\n")
    course = ask_course(system, "Course that needs a prerequisite (e.g. CS303): ")
    if course is None:
        return
    prereq = ask_course(system, f"Course that must be passed BEFORE {course.course_code} (e.g. CS201): ")
    if prereq is None:
        return
    ok, message = system.add_prerequisite(course, prereq)
    lines = [message]
    if ok:
        lines += [SEPARATOR, f"Prerequisites of {course.course_code} now:"]
        lines += course_list_lines(system.prerequisites_of(course))
    print()
    print_box("PREREQUISITE ADDED" if ok else "NOT ADDED", lines)


def remove_prerequisite(system):
    """(d) Course X removes course Y as a prerequisite = remove edge Y -> X."""
    print_title("REMOVE A PREREQUISITE")
    course = ask_course(system, "Course to remove a prerequisite from (e.g. CS301): ")
    if course is None:
        return
    current = system.prerequisites_of(course)
    print(f"Current prerequisites of {course.course_code}: "
          f"{', '.join(c.course_code for c in current) or '(none)'}")
    if not current:
        return
    prereq = ask_course(system, f"Prerequisite to remove from {course.course_code} (e.g. "
                                f"{current[0].course_code}): ")
    if prereq is None:
        return
    print()
    if system.remove_prerequisite(course, prereq):
        print_box("PREREQUISITE REMOVED",
                  [f"{prereq.course_code} is no longer a prerequisite of {course.course_code}.", SEPARATOR,
                   f"Prerequisites of {course.course_code} now:"]
                  + course_list_lines(system.prerequisites_of(course)))
    else:
        print(f"{prereq.course_code} is not a prerequisite of {course.course_code}.")



# Extra features
def view_prerequisite_tree(system):
    """Every course needed before this one: direct AND indirect (depth-first)."""
    print_title("FULL PREREQUISITE TREE")
    course = ask_course(system)
    if course is None:
        return
    tree = tree_lines(course, system.prerequisites_of, label)
    every = system.all_prerequisites(course)
    print_box(f"EVERYTHING NEEDED BEFORE {course.course_code}", tree + [SEPARATOR,
              f"Direct prerequisites : {len(system.prerequisites_of(course))}",
              f"All prerequisites    : {len(every)}  ({', '.join(c.course_code for c in every) or 'none'})"])


def view_study_plan(system):
    """Courses by year, prerequisites first (Kahn's algorithm), and a check of the plan."""
    plan, notes = system.plan_by_year()
    print_title("STUDY PLAN BY YEAR")
    if plan is None:
        print(notes[0])
        return
    rows = []
    for year, courses in plan:
        for i, c in enumerate(courses):
            needs = ", ".join(p.course_code for p in system.prerequisites_of(c)) or "-"
            rows.append([f"Year {year}" if i == 0 else "", c.course_code, c.course_name,
                         c.credit_hours, needs])
    print_table(["Year", "Code", "Course Name", "Credits", "Needs"], rows, right_align=(3,))

    year_credits = " | ".join(f"Year {year}: {sum(c.credit_hours for c in courses)} credits"
                         for year, courses in plan)
    check = notes or ["OK: every prerequisite is taken in an earlier year."]
    print_box("PLAN CHECK", [year_credits, SEPARATOR] + check)


def view_prerequisite_map(system):
    """The whole graph as a table, and an option to save it as a picture."""
    rows = []
    for c in system.courses():
        needs = ", ".join(p.course_code for p in system.prerequisites_of(c)) or "-"
        unlocks = ", ".join(u.course_code for u in system.unlocked_by(c)) or "-"
        rows.append([c.course_code, c.course_name, c.level, needs, unlocks])
    print_title(f"PREREQUISITE MAP ({system.graph.vertexCount()} courses, "
                f"{system.graph.edgeCount()} prerequisite links)")
    print_table(["Code", "Course Name", "Level", "Requires", "Unlocks"], rows)

    if input("\nSave the graph as a picture? (y/n): ").strip().lower() in ("y", "yes"):
        ok, result = save_graph_picture(system, GRAPH_PICTURE)
        if ok:
            print(f"Picture saved to {result}")
            open_file(result)                  # opens it on Windows
        else:
            print(f"Could not save the picture: {result}")



# Menu
# Each group has a heading and its options. The options are numbered 1, 2, 3 ...
# in this order, so to add an option just add one line to a group.
MENU_GROUPS = [
    ("BROWSE COURSES", [
        ("View All Courses", view_all_courses),
        ("View Course Details", view_course_details),
        ("View Prerequisites of a Course", view_prerequisites),
        ("View Courses Unlocked by a Course", view_unlocked_courses),
    ]),
    ("MANAGE COURSES", [
        ("Add a New Course", add_new_course),
        ("View Course Profile (Core / Elective)", view_course_profile),
        ("Add a Prerequisite to a Course", add_prerequisite),
        ("Remove a Prerequisite from a Course", remove_prerequisite),
    ]),
    ("PLAN YOUR STUDIES", [
        ("View Full Prerequisite Tree", view_prerequisite_tree),
        ("View Study Plan by Year", view_study_plan),
        ("View Prerequisite Map / Save Graph Picture", view_prerequisite_map),
    ]),
]

# One flat list of all options, in menu order: MENU[0] is option 1, MENU[1] is option 2 ...
MENU = [option for _, options in MENU_GROUPS for option in options]


def menu_lines(system):
    """The lines of the menu box: every group heading with its numbered options."""
    lines = [f"{system.graph.vertexCount()} courses | {system.graph.edgeCount()} prerequisite links", SEPARATOR]
    number = 1
    for heading, options in MENU_GROUPS:
        lines.append(heading)
        for text, _ in options:
            lines.append(f"  {number:>2}. {text}")
            number += 1
        lines.append(SEPARATOR)
    lines.append(f"  {number:>2}. Exit")
    return lines


def main():
    system = build_initial_system()
    exit_option = str(len(MENU) + 1)            # always the number after the last option

    while True:
        print()
        print_box("UNIVERSITY COURSE PREREQUISITE SYSTEM", menu_lines(system))

        choice = ""
        while choice == "":                      # an empty Enter is ignored
            choice = input("Enter choice: ").strip()

        if choice == exit_option:
            print("\nExiting program. Goodbye!")
            break
        if choice.isdigit() and 1 <= int(choice) <= len(MENU):
            print()
            MENU[int(choice) - 1][1](system)     # call the chosen function
            pause()
        else:
            print(f"Invalid choice, please enter 1-{exit_option}.")


if __name__ == "__main__":
    main()
