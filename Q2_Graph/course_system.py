"""
STEP 4 - course_system.py
=========================
The course-prerequisite SYSTEM: it connects the generic Graph to the
Course entity and adds the university's rules.

    edge direction:  prerequisite  ->  course it unlocks

    prerequisites of X       = INCOMING adjacent vertices of X
    courses unlocked by X    = OUTGOING adjacent vertices of X

Rules added here (the Graph itself has no rules about courses):
    - at most MAX_COURSES courses (the brief allows 5 to 10)
    - a course code must be unique
    - a course cannot be its own prerequisite
    - a prerequisite cannot be added twice
    - no CYCLES: if CS301 needs CS201, then CS201 can never need CS301,
      otherwise no student could ever take either course
"""

from course_data import INITIAL_COURSES, INITIAL_PREREQUISITES
from graph import Graph

MAX_COURSES = 10


class CourseSystem:

    def __init__(self):
        self.graph = Graph()       # vertices are Course objects
        self.catalogue = {}        # course code -> Course, to find a course by its code fast


    # Finding and adding courses
    def get(self, code):
        """Find a course by its code. Spaces and lower case are allowed: ' cs201' works."""
        return self.catalogue.get(code.strip().upper())

    def courses(self):
        return self.graph.getVertices()

    def add_course(self, course):
        """Add a course as a new vertex. Returns (True/False, message)."""
        if len(self.catalogue) >= MAX_COURSES:
            return False, f"Cannot add more courses - the maximum is {MAX_COURSES}."
        if course.course_code in self.catalogue:
            return False, f"Course code {course.course_code} already exists."
        self.catalogue[course.course_code] = course
        self.graph.addVertex(course)
        return True, f"Course {course.course_code} - {course.course_name} added."


    # Prerequisites (edges)
    def add_prerequisite(self, course, prerequisite):
        """Make `prerequisite` required before `course` (edge prerequisite -> course).
        Returns (True/False, message)."""
        if course == prerequisite:
            return False, "A course cannot be a prerequisite of itself."
        if self.graph.hasEdge(prerequisite, course):
            return False, f"{prerequisite.course_code} is already a prerequisite of {course.course_code}."
        # If `course` already leads to `prerequisite`, the new edge would close a loop.
        if self.graph.hasPath(course, prerequisite):
            return False, (f"Rejected - this would create a cycle: {course.course_code} is already "
                           f"a direct or indirect prerequisite of {prerequisite.course_code}.")
        self.graph.addEdge(prerequisite, course)
        return True, f"{prerequisite.course_code} added as a prerequisite of {course.course_code}."

    def remove_prerequisite(self, course, prerequisite):
        """Remove the edge prerequisite -> course. Returns True if it existed."""
        return self.graph.removeEdge(prerequisite, course)


    # Questions the menu asks
    def prerequisites_of(self, course):
        return self.graph.listIncomingAdjacentVertex(course)

    def unlocked_by(self, course):
        return self.graph.listOutgoingAdjacentVertex(course)

    def all_prerequisites(self, course):
        """Direct AND indirect prerequisites, sorted by code."""
        return sorted(self.graph.allIncomingReachable(course), key=lambda c: c.course_code)

    def study_plan(self):
        """Courses grouped into levels by Kahn's algorithm: a course appears only after
        ALL its prerequisites. Used to put courses in a correct order."""
        levels = self.graph.topologicalOrder()
        if levels is None:
            return None
        return [sorted(level, key=lambda c: c.course_code) for level in levels]


    def plan_by_year(self):

        levels = self.study_plan()
        if levels is None:
            return None, ["No plan is possible because the prerequisites form a cycle."]
        order = {course: number for number, level in enumerate(levels) for course in level}

        years = sorted({c.year for c in self.courses()})
        plan = [(year, sorted([c for c in self.courses() if c.year == year],
                              key=lambda c: (order[c], c.course_code)))
                for year in years]

        notes = []
        for course in self.courses():
            for prereq in self.prerequisites_of(course):
                if prereq.year > course.year:
                    notes.append(f"PROBLEM: {course.course_code} (Year {course.year}) needs "
                                 f"{prereq.course_code}, which is only in Year {prereq.year}.")
                elif prereq.year == course.year:
                    notes.append(f"NOTE: {course.course_code} needs {prereq.course_code} in the same "
                                 f"year (Year {course.year}) - take {prereq.course_code} first.")
        return plan, notes


def build_initial_system():
    """Create the system with the pre-defined courses and prerequisite links."""
    system = CourseSystem()
    for course in INITIAL_COURSES:
        system.add_course(course)
    for prereq_code, course_code in INITIAL_PREREQUISITES:
        system.add_prerequisite(system.get(course_code), system.get(prereq_code))
    return system


# Quick test
if __name__ == "__main__":
    s = build_initial_system()
    cs301 = s.get("cs301")
    print("Courses:", s.graph.vertexCount(), "| links:", s.graph.edgeCount())
    print("CS301 needs     :", s.prerequisites_of(cs301))
    print("CS301 needs all :", s.all_prerequisites(cs301))
    print("CS201 unlocks   :", s.unlocked_by(s.get("CS201")))
    print("Cycle test      :", s.add_prerequisite(s.get("CS101"), cs301)[1])
    print("Plan by year    :", s.plan_by_year())