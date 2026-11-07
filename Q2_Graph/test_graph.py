"""
STEP 7 - test_graph.py  -  automatic tests for the Graph and the CourseSystem
=============================================================================
Run it like any other file (right-click -> Run). "OK" means every test passed.
The Graph tests use plain strings as vertices, which also proves the Graph is
generic (it works without the Course class).
"""

import unittest

from course import CORE, ELECTIVE, Course
from course_system import MAX_COURSES, build_initial_system
from graph import Graph


class TestGraph(unittest.TestCase):

    def __str__(self):
        return self._testMethodName          # show only the test name in the output

    def setUp(self):
        """Runs before EVERY test: A -> C, B -> C, C -> D"""
        self.g = Graph()
        for v in ("A", "B", "C", "D"):
            self.g.addVertex(v)
        self.g.addEdge("A", "C")
        self.g.addEdge("B", "C")
        self.g.addEdge("C", "D")

    def test_add_vertex_twice_is_rejected(self):
        self.assertFalse(self.g.addVertex("A"))
        self.assertEqual(self.g.vertexCount(), 4)

    def test_list_incoming_and_outgoing(self):
        self.assertEqual(self.g.listIncomingAdjacentVertex("C"), ["A", "B"])
        self.assertEqual(self.g.listOutgoingAdjacentVertex("C"), ["D"])
        self.assertEqual(self.g.listIncomingAdjacentVertex("A"), [])

    def test_self_loop_and_duplicate_edge_rejected(self):
        self.assertFalse(self.g.addEdge("A", "A"))
        self.assertFalse(self.g.addEdge("A", "C"))
        self.assertEqual(self.g.edgeCount(), 3)

    def test_unknown_vertex_raises_error(self):
        with self.assertRaises(KeyError):
            self.g.addEdge("A", "Z")

    def test_remove_edge_updates_both_lists(self):
        self.assertTrue(self.g.removeEdge("A", "C"))
        self.assertNotIn("C", self.g.listOutgoingAdjacentVertex("A"))
        self.assertNotIn("A", self.g.listIncomingAdjacentVertex("C"))
        self.assertFalse(self.g.removeEdge("A", "C"))          # already removed

    def test_returned_list_is_a_copy(self):
        self.g.listIncomingAdjacentVertex("C").append("X")     # change the copy ...
        self.assertEqual(self.g.listIncomingAdjacentVertex("C"), ["A", "B"])   # ... graph unchanged

    def test_has_path(self):
        self.assertTrue(self.g.hasPath("A", "D"))               # A -> C -> D
        self.assertFalse(self.g.hasPath("D", "A"))              # edges have a direction

    def test_all_incoming_reachable(self):
        self.assertEqual(sorted(self.g.allIncomingReachable("D")), ["A", "B", "C"])

    def test_topological_order(self):
        self.assertEqual(self.g.topologicalOrder(), [["A", "B"], ["C"], ["D"]])

    def test_topological_order_detects_cycle(self):
        self.g.addEdge("D", "A")                                # A -> C -> D -> A
        self.assertIsNone(self.g.topologicalOrder())


class TestCourseSystem(unittest.TestCase):

    def __str__(self):
        return self._testMethodName

    def setUp(self):
        self.s = build_initial_system()

    def test_initial_data_loaded(self):
        self.assertEqual(self.s.graph.vertexCount(), 8)
        self.assertEqual(self.s.graph.edgeCount(), 10)

    def test_course_code_is_case_insensitive(self):
        self.assertIs(self.s.get(" cs201 "), self.s.get("CS201"))

    def test_prerequisites_and_unlocked(self):
        codes = lambda courses: [c.course_code for c in courses]
        self.assertEqual(codes(self.s.prerequisites_of(self.s.get("CS301"))), ["CS201", "CS102"])
        self.assertEqual(codes(self.s.unlocked_by(self.s.get("CS201"))), ["CS301", "CS302"])

    def test_cycle_is_rejected(self):
        ok, _ = self.s.add_prerequisite(self.s.get("CS101"), self.s.get("CS301"))
        self.assertFalse(ok)
        self.assertEqual(self.s.graph.edgeCount(), 10)          # nothing was added

    def test_maximum_ten_courses(self):
        for i in range(MAX_COURSES - 8):                        # fill up to 10 courses
            self.assertTrue(self.s.add_course(Course(f"CS9{i}", "X", 3, CORE, 1, "-"))[0])
        ok, _ = self.s.add_course(Course("CS999", "Too many", 3, ELECTIVE, 1, "-"))
        self.assertFalse(ok)

    def test_study_plan_respects_every_prerequisite(self):
        stage_of = {}
        for number, stage in enumerate(self.s.study_plan()):
            for course in stage:
                stage_of[course] = number
        for course in self.s.courses():
            for prereq in self.s.prerequisites_of(course):
                self.assertLess(stage_of[prereq], stage_of[course])


    def test_plan_by_year_initial_data_is_valid(self):
        plan, notes = self.s.plan_by_year()
        self.assertEqual([year for year, _ in plan], [1, 2, 3])
        self.assertEqual(notes, [])                             # no problems in the sample data

    def test_plan_by_year_reports_same_year_prerequisite(self):
        self.s.add_prerequisite(self.s.get("CS202"), self.s.get("CS201"))   # both Year 2
        plan, notes = self.s.plan_by_year()
        year2 = [c.course_code for c in plan[1][1]]
        self.assertLess(year2.index("CS201"), year2.index("CS202"))      # CS201 listed first
        self.assertEqual(len(notes), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)        # verbosity=2 prints the name of every test