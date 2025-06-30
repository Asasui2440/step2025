#!/usr/bin/env python3

import sys
import math
import random

from common import print_tour, read_input


def distance(city1: tuple[float, float], city2: tuple[float, float]) -> float:
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)


def distance_matrix(cities: list[tuple[float, float]]) -> list[list[float]]:
    n = len(cities)
    dist_matrix = [[0.0] * n for i in range(n)]
    for i in range(n):
        for j in range(i, n):
            dist_matrix[i][j] = dist_matrix[j][i] = distance(cities[i], cities[j])
    return dist_matrix


def total_distance(tour: list[int], dist_matrix: list[list[float]]) -> float:
    total_dist = 0.0
    for i in range(len(tour) - 1):
        node_index = tour[i]
        node_next_index = tour[i + 1]

        total_dist += dist_matrix[node_index][node_next_index]

    total_dist += dist_matrix[tour[-1]][tour[0]]
    return total_dist


def solve_opt2(tour: list[int], dist_matrix: list[list[float]]) -> list[int]:
    tour = tour[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(tour) - 2):
            for j in range(i + 1, len(tour) - 1):
                a, b = tour[i - 1], tour[i]
                c, d = tour[j], tour[j + 1]
                if (
                    dist_matrix[a][b] + dist_matrix[c][d]
                    > dist_matrix[a][c] + dist_matrix[b][d]
                ):
                    tour[i : j + 1] = reversed(tour[i : j + 1])
                    improved = True

    return tour

# 貪欲法を、min(200,N)個の開始点で試して一番良いtourを選ぶ
def solve_greedy_multi_start(dist_matrix: list[list[float]]) -> list[int]:
    N = len(dist_matrix)
    start_points = random.sample(range(N), min(200, N))
    best_tour = None
    best_distance = float("inf")

    for start in start_points:
        current_city = start
        unvisited_cities = set(range(N))
        tour = [current_city]
        unvisited_cities.remove(current_city)

        while unvisited_cities:
            next_city = min(
                unvisited_cities, key=lambda city: dist_matrix[current_city][city]
            )
            tour.append(next_city)
            unvisited_cities.remove(next_city)
            current_city = next_city

        dist = total_distance(tour, dist_matrix)
        if dist < best_distance:
            best_tour = tour[:]
            best_distance = dist

    return best_tour

# 3本の辺を取って組み替える
def three_opt(tour: list[int], dist_matrix: list[list[float]]):
    n = len(tour)
    while True:
        a, b, c = sorted(random.sample(range(n), 3))
        if b - a > 1 and c - b > 1:  # 適切な間隔を保つ
            break

    P1 = tour[:a]
    P2 = tour[a:b]
    P3 = tour[b:c]
    P4 = tour[c:]

    patterns = [
        P1 + P3 + P2 + P4,
        P1 + list(reversed(P2)) + list(reversed(P3)) + P4,
        P1 + P3 + list(reversed(P2)) + P4,
        P1 + list(reversed(P3)) + P2 + P4,
        P1 + list(reversed(P3)) + list(reversed(P2)) + P4,
    ]

    best_tour = patterns[0]
    best_score = total_distance(best_tour, dist_matrix)

    for tour in patterns[1:]:
        dist = total_distance(tour, dist_matrix)
        if dist < best_score:
            best_tour = tour[:]
            best_score = dist

    return best_tour

# three_optを10万回実行
def solve_opt3_random(
    tour: list[int],
    dist_matrix: list[list[float]],
    iterations: int = 100000,
) -> list[int]:
    """ランダム3-opt最適化 - O(iterations)"""
    best_tour = tour[:]
    best_cost = total_distance(best_tour, dist_matrix)

    for _ in range(iterations):
        new_tour = three_opt(best_tour, dist_matrix)
        new_cost = total_distance(new_tour, dist_matrix)

        if new_cost < best_cost:
            best_tour = new_tour
            best_cost = new_cost

    return best_tour


# ランダムに、長さ1~3の1つの辺を取ってきて、どこかに挿入する
def or_opt(tour: list[int], dist_matrix: list[list[float]]):
    best_tour = tour[:]
    best_cost = total_distance(tour, dist_matrix)

    n = len(tour)
    for _ in range(10):
        segment_length = random.randint(1, min(3, n - 1))
        i = random.randint(0, n - segment_length)
        j = i + segment_length
        segment = tour[i:j]
        rest = tour[:i] + tour[j:]

        insert_pos = random.randint(0, len(rest))
        new_tour = rest[:insert_pos] + segment + rest[insert_pos:]
        new_cost = total_distance(new_tour, dist_matrix)

        if new_cost < best_cost:
            best_tour = new_tour[:]
            best_cost = new_cost
    return best_tour


# 2本の辺を取ってきて交換。10回やっていちばんいいtourを返す
def two_opt(tour: list[int], dist_matrix: list[list[float]]) -> list[int]:
    best_tour = tour[:]
    best_cost = total_distance(tour, dist_matrix)
    n = len(tour)
    for _ in range(10):
        i, j = sorted(random.sample(range(n), 2))
        if j - i <= 1:
            j = (j + 1) % n
        new_tour = tour[:i] + list(reversed(tour[i : j + 1])) + tour[j + 1 :]
        new_cost = total_distance(new_tour, dist_matrix)
        if new_cost < best_cost:
            best_tour = new_tour
            best_cost = new_cost
    return best_tour


# アニーリング
def solve_annealing(
    tour: list[int],
    dist_matrix: list[list[float]],
    initial_temp=None,
    final_temp=1e-7,
    alpha=0.9999,
    max_iter=int(1e7),
) -> list[int]:
    
    def neighbor(tour):
        p = random.random()
        if p < 0.35:
            return two_opt(tour, dist_matrix)
        elif p < 0.65:
            return three_opt(tour, dist_matrix)
        else:
            return or_opt(tour, dist_matrix)
        
    current_tour = tour[:]
    best_tour = tour[:]
    current_cost = total_distance(current_tour, dist_matrix)
    best_cost = current_cost

    if initial_temp is None:
        initial_temp = current_cost * 0.3

    temp = initial_temp

    for iter in range(max_iter):
        if iter % 50000 == 0 and iter < 1e7:
            print("iter = ", iter)
            print("temp= ",temp)
        
        new_tour = neighbor(current_tour)
        new_cost = total_distance(new_tour,dist_matrix)

        delta = new_cost - current_cost

        if delta < 0 or math.exp(-delta / temp) > random.random():
            # if delta < 0:
            #    print(f"iter: {iter}, temp: {temp}, delta: {delta}")
            current_tour = new_tour[:]
            current_cost = new_cost
            if current_cost < best_cost:
                best_tour = current_tour[:]
                best_cost = current_cost

        temp *= alpha
        #print("new_temp= ",temp)
        if temp < final_temp:
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

    tour = solve_annealing(tour,dist_matrix)
    print("annealing = ", total_distance(tour, dist_matrix))

    tour = solve_opt3_random(tour, dist_matrix)
    print("opt3 = ", total_distance(tour, dist_matrix))

    # print_tour(tour)
