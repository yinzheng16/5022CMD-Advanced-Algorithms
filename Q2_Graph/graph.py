"""
STEP 1 - graph.py
=================
My own UNWEIGHTED DIRECTED GRAPH.

    A ----> B      "an edge from A to B"
                   (for courses: A is a prerequisite of B, so passing A unlocks B)

HOW THE GRAPH IS STORED (adjacency lists in two dictionaries)
-------------------------------------------------------------
    outgoing[v] = list of vertices that v points TO      (edges v -> x)
    incoming[v] = list of vertices that point TO v       (edges x -> v)

Example with edges CS101 -> CS201 and CS102 -> CS201:
    outgoing = {CS101: [CS201], CS102: [CS201], CS201: []}
    incoming = {CS101: [],      CS102: [],      CS201: [CS101, CS102]}

Keeping BOTH directions uses a little more memory, but then
"list incoming" and "list outgoing" are both fast: we just read one list,
instead of searching through every vertex in the graph.

This class is GENERIC: a vertex can be any hashable object (a string, a
number, a Course ...). It never imports Course, so it can be reused for any
other problem, e.g. cities and roads, or tasks that depend on other tasks.

Method names addVertex / addEdge / listIncomingAdjacentVertex follow the brief.
"""

from collections import deque


class Graph:

    def __init__(self):
        self.outgoing = {}    # vertex -> list of vertices it points to
        self.incoming = {}    # vertex -> list of vertices that point to it

    # Required by the brief
    def addVertex(self, vertex):
        """Add a new vertex with no edges. Returns False if it already exists."""
        if vertex in self.outgoing:
            return False
        self.outgoing[vertex] = []
        self.incoming[vertex] = []
        return True

    def addEdge(self, from_vertex, to_vertex):
        """Add the directed edge  from_vertex -> to_vertex.
        Returns False for a self-loop (A -> A) or an edge that already exists.
        Raises KeyError if either vertex is not in the graph."""
        self.check_vertex(from_vertex)
        self.check_vertex(to_vertex)
        if from_vertex == to_vertex or to_vertex in self.outgoing[from_vertex]:
            return False
        self.outgoing[from_vertex].append(to_vertex)   # update BOTH lists,
        self.incoming[to_vertex].append(from_vertex)   # so they always agree
        return True

    def listIncomingAdjacentVertex(self, vertex):
        """All vertices that have an edge coming INTO vertex.
        A copy is returned, so the caller cannot change the graph by accident."""
        self.check_vertex(vertex)
        return list(self.incoming[vertex])

    # Extra methods
    def listOutgoingAdjacentVertex(self, vertex):
        """All vertices that vertex has an edge going OUT to."""
        self.check_vertex(vertex)
        return list(self.outgoing[vertex])

    def removeEdge(self, from_vertex, to_vertex):
        """Remove the edge from_vertex -> to_vertex. Returns False if it does not exist."""
        self.check_vertex(from_vertex)
        self.check_vertex(to_vertex)
        if to_vertex not in self.outgoing[from_vertex]:
            return False
        self.outgoing[from_vertex].remove(to_vertex)
        self.incoming[to_vertex].remove(from_vertex)
        return True

    def hasVertex(self, vertex):
        return vertex in self.outgoing

    def hasEdge(self, from_vertex, to_vertex):
        return self.hasVertex(from_vertex) and to_vertex in self.outgoing[from_vertex]

    def hasPath(self, start, goal):

        self.check_vertex(start)
        self.check_vertex(goal)
        visited = {start}
        queue = deque([start])            # deque: fast to take items from the front
        while queue:
            current = queue.popleft()
            if current == goal:
                return True
            for neighbour in self.outgoing[current]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)
        return False

    def allIncomingReachable(self, vertex):
        self.check_vertex(vertex)
        found = []
        stack = list(self.incoming[vertex])
        while stack:
            current = stack.pop()
            if current not in found:
                found.append(current)
                stack.extend(self.incoming[current])
        return found

    def topologicalOrder(self):

        remaining = {v: len(self.incoming[v]) for v in self.outgoing}   # in-degree
        level = [v for v, count in remaining.items() if count == 0]
        levels = []
        done = 0
        while level:
            levels.append(level)
            done += len(level)
            next_level = []
            for v in level:
                for w in self.outgoing[v]:
                    remaining[w] -= 1          # one of w's prerequisites is now done
                    if remaining[w] == 0:
                        next_level.append(w)
            level = next_level
        if done != len(self.outgoing):         # some vertices never reached 0 -> cycle
            return None
        return levels

    def getVertices(self):
        return list(self.outgoing)

    def vertexCount(self):
        return len(self.outgoing)

    def edgeCount(self):
        return sum(len(targets) for targets in self.outgoing.values())

    def check_vertex(self, vertex):
        if vertex not in self.outgoing:
            raise KeyError(f"Vertex {vertex!r} is not in the graph")



# Quick test - run this file directly (right-click graph.py -> Run)
# The vertices here are plain strings, which shows the graph is generic.
if __name__ == "__main__":
    g = Graph()
    for v in ("A", "B", "C", "D"):
        g.addVertex(v)
    g.addEdge("A", "C")        # A -> C
    g.addEdge("B", "C")        # B -> C
    g.addEdge("C", "D")        # C -> D

    print("Incoming to C :", g.listIncomingAdjacentVertex("C"))   # ['A', 'B']
    print("Outgoing from C:", g.listOutgoingAdjacentVertex("C"))  # ['D']
    print("Path A -> D?   :", g.hasPath("A", "D"))                # True
    print("All before D   :", g.allIncomingReachable("D"))        # C, B, A
    print("Levels         :", g.topologicalOrder())               # [['A','B'], ['C'], ['D']]
    print("Vertices/edges :", g.vertexCount(), "/", g.edgeCount())