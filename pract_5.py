import heapq

class Node:
    def __init__(self, state, g, h, parent=None):
        self.state = state
        self.g = g  # actual cost
        self.h = h  # heuristic
        self.f = g + h
        self.parent = parent

    def __lt__(self, other):
        return self.f < other.f


def heuristic(state, goal):
    return len(goal) - len(state)


def get_successors(state, resources, goal):
    successors = []
    for r in resources:
        if r not in state and r in goal:
            new_state = state + [r]
            successors.append(new_state)
    return successors


def reconstruct_path(node):
    path = []
    while node:
        path.append(node.state)
        node = node.parent
    return list(reversed(path))


def a_star(resources, goal):
    start = Node([], 0, heuristic([], goal))
    open_list = []
    heapq.heappush(open_list, start)
    closed = set()

    while open_list:
        current = heapq.heappop(open_list)
        if set(current.state) == set(goal):
            return reconstruct_path(current), current.g
        closed.add(tuple(current.state))
        for succ in get_successors(current.state, resources, goal):
            g = current.g + 1
            h = heuristic(succ, goal)
            child = Node(succ, g, h, current)
            if tuple(succ) not in closed:
                heapq.heappush(open_list, child)
    return None, float("inf")


if __name__ == "__main__":
    print("=== Logistics Resource Allocation using A* ===")
    n = int(input("Enter total number of resources: "))
    resources = [input(f"Enter resource {i+1}: ").strip() for i in range(n)]
    goal = input("Enter required resources for allocation (comma separated): ").split(",")
    goal = [g.strip() for g in goal if g.strip()]

    path, cost = a_star(resources, goal)
    print("\nOptimal Allocation Path:")
    for step in path:
        print(" ", step)
    print("Total Cost:", cost)
