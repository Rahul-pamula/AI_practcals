# logistics_ao_star.py
# AO* algorithm for resource allocation on an AND-OR graph

from typing import Dict, List, Tuple, Optional

class Relation:
    def __init__(self, rtype: str, cost: float, children: List[str]):
        rtype = rtype.strip().upper()
        if rtype not in ("AND", "OR"):
            raise ValueError("Relation type must be AND or OR")
        self.type = rtype
        self.cost = float(cost)
        self.children = children  # list of child node names

    def __repr__(self):
        return f"Relation(type={self.type}, cost={self.cost}, children={self.children})"


Graph = Dict[str, List[Relation]]
Heuristics = Dict[str, float]
Memo = Dict[str, Tuple[float, Optional[Relation]]]  # node -> (min_cost, chosen_relation)


def ao_star(node: str, graph: Graph, h: Heuristics, memo: Memo) -> Tuple[float, Optional[Relation]]:
    """
    Compute minimal cost from 'node' to solve the AND-OR graph using AO* cost backup.
    Returns (best_cost, best_relation). If the node is terminal (no relations),
    best_relation is None and cost equals heuristic h[node].
    """
    if node in memo:
        return memo[node]

    relations = graph.get(node, [])
    # Terminal / leaf node: cost = heuristic
    if not relations:
        cost = float(h.get(node, 0.0))
        memo[node] = (cost, None)
        return memo[node]

    best_cost = float("inf")
    best_rel: Optional[Relation] = None

    for rel in relations:
        if rel.type == "AND":
            # For AND: take all children
            total = rel.cost
            for c in rel.children:
                c_cost, _ = ao_star(c, graph, h, memo)
                total += c_cost
        else:  # "OR"
            # For OR: choose the cheapest child
            if not rel.children:
                total = rel.cost  # degenerate OR with no children
            else:
                child_costs = [ao_star(c, graph, h, memo)[0] for c in rel.children]
                total = rel.cost + min(child_costs)

        if total < best_cost:
            best_cost = total
            best_rel = rel

    memo[node] = (best_cost, best_rel)
    return memo[node]


def extract_plan(node: str, memo: Memo) -> List[Tuple[str, str, float, List[str]]]:
    """
    Reconstruct the optimal AND-OR plan as a list of tuples:
    (parent_node, relation_type, relation_cost, children)
    """
    if node not in memo:
        return []
    _, rel = memo[node]
    plan: List[Tuple[str, str, float, List[str]]] = []
    if rel is None:
        return plan  # terminal

    plan.append((node, rel.type, rel.cost, rel.children[:]))

    if rel.type == "AND":
        # Include plans for all children
        for c in rel.children:
            plan.extend(extract_plan(c, memo))
    else:  # OR
        # Follow only the chosen cheapest child
        if rel.children:
            # Pick the child with minimal memoized cost
            best_child = min(rel.children, key=lambda x: memo[x][0])
            plan.extend(extract_plan(best_child, memo))
    return plan


def pretty_print_solution(root: str, memo: Memo):
    total_cost, _ = memo[root]
    plan = extract_plan(root, memo)

    print("\n=== AO* Optimal Allocation Strategy ===")
    for parent, rtype, rcost, children in plan:
        if rtype == "AND":
            print(f"{parent} --AND({rcost})-> {children}")
        else:
            print(f"{parent} --OR({rcost})-> {children}")
    print(f"\nMinimum Total Cost from '{root}': {total_cost:.2f}")


if __name__ == "__main__":
    print("=== Logistics Resource Allocation using AO* (AND-OR Graph) ===")

    # Nodes & heuristics
    n = int(input("Enter total number of nodes: ").strip() or "0")
    h: Heuristics = {}
    for i in range(n):
        name = input(f" Node {i+1} name: ").strip()
        heu = float(input(f"  Heuristic h({name}): ").strip() or "0")
        h[name] = heu

    # Relations
    m = int(input("\nEnter number of relations: ").strip() or "0")
    graph: Graph = {}
    print(
        "\nFor each relation, provide:\n"
        " parent_node\n type (AND/OR)\n relation_cost (number)\n k = number of children\n child_1 ... child_k\n"
    )
    for j in range(m):
        print(f"\nRelation {j+1}:")
        parent = input(" parent_node: ").strip()
        rtype = input(" type (AND/OR): ").strip().upper()
        rcost = float(input(" relation_cost: ").strip() or "0")
        k = int(input(" number of children (k): ").strip() or "0")
        children = []
        for t in range(k):
            children.append(input(f"  child_{t+1}: ").strip())
        rel = Relation(rtype, rcost, children)
        graph.setdefault(parent, []).append(rel)

    root = input("\nEnter root/start node: ").strip()
    if root not in h:
        print(f"[Warning] Root '{root}' has no heuristic specified. Using 0 by default.")
        h[root] = 0.0

    memo: Memo = {}
    ao_star(root, graph, h, memo)
    pretty_print_solution(root, memo)
