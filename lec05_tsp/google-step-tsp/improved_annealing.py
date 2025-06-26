import random
import time
import math
import sys

from common import print_tour, read_input
from solver_opt import (
    total_distance,
    solve_greedy_multi_start,
    solve_opt2,
    two_opt,
    three_opt,
    or_opt,
    distance_matrix,
)
from solve_opt3 import solve_3opt_random


def solve_improved_annealing(
    tour: list[int], dist_matrix: list[list[float]], time_limit=100
) -> list[int]:
    """改善された焼きなまし法"""

    def neighbor(tour):
        p = random.random()
        if p < 0.4:
            return two_opt(tour, dist_matrix)
        elif p < 0.7:
            return three_opt(tour, dist_matrix)
        else:
            return or_opt(tour, dist_matrix)

    def cost(tour):
        return total_distance(tour, dist_matrix)

    best_tour = tour[:]
    current = tour[:]
    best_cost = cost(best_tour)

    start_time = time.time()

    current_cost = cost(current)

    # 適応的な温度パラメータ
    initial_temp = current_cost * 0.1
    final_temp = 1e-5
    alpha = 0.95

    t = initial_temp
    no_improve_count = 0

    while t > final_temp and time.time() - start_time < time_limit:
        for _ in range(100):  # 各温度で複数回試行
            new_tour = neighbor(current)
            new_cost = cost(new_tour)

            delta = new_cost - current_cost

            if delta < 0 or random.random() < math.exp(-delta / t):
                current = new_tour
                current_cost = new_cost

                if current_cost < best_cost:
                    best_tour = current[:]
                    best_cost = current_cost
                    no_improve_count = 0
                else:
                    no_improve_count += 1

        t *= alpha

        # 局所最適解に陥った場合のリスタート
        if no_improve_count > 1000:
            break

    return best_tour


if __name__ == "__main__":
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    dist_matrix = distance_matrix(cities)
    tour = solve_greedy_multi_start(dist_matrix)
    print("greedy = ", total_distance(tour, dist_matrix))
    tour = solve_opt2(tour, dist_matrix)
    print("opt2 = ", total_distance(tour, dist_matrix))

    tour = solve_improved_annealing(tour, dist_matrix)
    print("annealing = ", total_distance(tour, dist_matrix))

    tour = solve_3opt_random(tour, dist_matrix)
    print("opt3 = ", total_distance(tour, dist_matrix))

    # print_tour(tour)
