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


# 交差を解消する
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

# 貪欲法を、min(30,N)個の開始点で試して一番良いtourを選ぶ
def solve_greedy_multi_start(dist_matrix: list[list[float]]) -> list[int]:
    N = len(dist_matrix)
    start_points = random.sample(range(N), min(30, N))
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




if __name__ == "__main__":
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    dist_matrix = distance_matrix(cities)

    tour = solve_greedy_multi_start(dist_matrix)
    print("greedy = ", total_distance(tour, dist_matrix))

    tour = solve_opt2(tour, dist_matrix)
    print("opt2 = ", total_distance(tour, dist_matrix))

    # print_tour(tour)
