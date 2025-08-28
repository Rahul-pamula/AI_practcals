# hill_climbing_inventory.py
import math, random, statistics, heapq
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SKU:
    name: str
    demand_mean: float
    holding_cost: float
    stockout_cost: float
    max_base: int = 100


@dataclass
class GlobalParams:
    horizon: int = 30
    simulations: int = 100
    fixed_order_cost: float = 5.0
    seed: int = 42


@dataclass(frozen=True)
class Solution:
    base_stock: Tuple[int, ...]


class InventoryProblem:
    def __init__(self, skus: List[SKU], gp: GlobalParams):
        self.skus = skus
        self.gp = gp
        random.seed(gp.seed)

    def _poisson(self, lam: float) -> int:
        L, k, p = math.exp(-lam), 0, 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    def evaluate(self, s: Solution) -> float:
        """Monte Carlo evaluation of expected cost."""
        results = []
        for _ in range(self.gp.simulations):
            inv = list(s.base_stock)
            total = 0
            for _ in range(self.gp.horizon):
                # Order up to base stock
                order = [max(0, s.base_stock[i] - inv[i]) for i in range(len(self.skus))]
                if sum(order) > 0:
                    total += self.gp.fixed_order_cost
                inv = [inv[i] + order[i] for i in range(len(self.skus))]

                # Demand
                demand = [self._poisson(sku.demand_mean) for sku in self.skus]
                sales = [min(inv[i], demand[i]) for i in range(len(self.skus))]
                lost = [demand[i] - sales[i] for i in range(len(self.skus))]
                inv = [inv[i] - sales[i] for i in range(len(self.skus))]

                total += sum(
                    self.skus[i].holding_cost * inv[i] +
                    self.skus[i].stockout_cost * lost[i]
                    for i in range(len(self.skus))
                )
            results.append(total)
        return statistics.mean(results)

    def neighbors(self, s: Solution):
        nbrs = []
        b = list(s.base_stock)
        for i, sku in enumerate(self.skus):
            if b[i] > 0:
                nb = b.copy()
                nb[i] -= 1
                nbrs.append(Solution(tuple(nb)))
            if b[i] < sku.max_base:
                nb = b.copy()
                nb[i] += 1
                nbrs.append(Solution(tuple(nb)))
        return nbrs


# Hill Climbing Algorithm
def hill_climbing(problem: InventoryProblem, start: Solution):
    current, cost = start, problem.evaluate(start)
    improved = True
    while improved:
        improved = False
        for n in problem.neighbors(current):
            nc = problem.evaluate(n)
            if nc < cost:
                current, cost = n, nc
                improved = True
                break
    return current, cost


# Best-First Search Algorithm
def best_first_search(problem: InventoryProblem, start: Solution, max_iter=100):
    visited = set()
    pq = []
    start_cost = problem.evaluate(start)
    heapq.heappush(pq, (start_cost, start))

    best_solution, best_cost = start, start_cost
    iterations = 0

    while pq and iterations < max_iter:
        cost, current = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)

        if cost < best_cost:
            best_solution, best_cost = current, cost

        for n in problem.neighbors(current):
            if n not in visited:
                nc = problem.evaluate(n)
                heapq.heappush(pq, (nc, n))

        iterations += 1

    return best_solution, best_cost


if __name__ == "__main__":
    n = int(input("Enter number of SKUs: "))
    skus = []
    start_base = []

    for i in range(n):
        print(f"\nEnter details for SKU {i+1}:")
        name = input(" Name: ")
        demand_mean = float(input(" Mean demand: "))
        holding_cost = float(input(" Holding cost per unit: "))
        stockout_cost = float(input(" Stockout cost per unit: "))
        max_base = int(input(" Max base stock: "))
        base_stock = int(input(" Starting base stock: "))

        skus.append(SKU(name, demand_mean, holding_cost, stockout_cost, max_base))
        start_base.append(base_stock)

    gp = GlobalParams()
    problem = InventoryProblem(skus, gp)
    start = Solution(tuple(start_base))

    sol1, cost1 = hill_climbing(problem, start)
    print("\nBest base-stock (Hill Climbing):", sol1.base_stock, "Expected cost:", round(cost1, 2))

    sol2, cost2 = best_first_search(problem, start)
    print("Best base-stock (Best-First Search):", sol2.base_stock, "Expected cost:", round(cost2, 2))

