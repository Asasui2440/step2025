#!/usr/bin/env python3

import sys
import math
import random

from common import format_tour, read_input


# 2つのcity間の距離を計算
def distance(city1: tuple[float, float], city2: tuple[float, float]) -> float:
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)


# 距離行列の作成
def distance_matrix(cities: list[tuple[float, float]]) -> list[list[float]]:
    n = len(cities)
    dist_matrix = [[0.0] * n for i in range(n)]
    for i in range(n):
        for j in range(i, n):
            dist_matrix[i][j] = dist_matrix[j][i] = distance(cities[i], cities[j])
    return dist_matrix


# ルートの総距離を計算
def total_distance(tour: list[int], dist_matrix: list[list[float]]) -> float:
    total_dist = 0.0
    for i in range(len(tour) - 1):
        city_index = tour[i]
        next_city_index = tour[i + 1]

        total_dist += dist_matrix[city_index][next_city_index]

    # 最後の点と開始点までの距離を最後に足す
    total_dist += dist_matrix[tour[-1]][tour[0]]
    return total_dist


# 多始点貪欲・開始点を変えて貪欲法を行う。一番いいルートを初期解として採用
# 引数 dist_matrix:距離行列、num_starts: 開始点を何個試すか


def solve_greedy_multi_start(
    dist_matrix: list[list[float]], num_starts: int
) -> list[int]:
    N = len(dist_matrix)

    start_points = []
    # num_startsが、都市の数より大きいなら、全ての都市で開始点を試す
    # そうでない時は開始点をランダムで選ぶ
    if N < num_starts:
        for i in range(N):
            start_points.append(i)
    else:
        start_points = random.sample(range(N), min(num_starts, N))

    best_tour = None
    best_dist = float("inf")

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
        if dist < best_dist:
            best_tour = tour[:]
            best_dist = dist

    return best_tour


# 2opt・ルートの全ての交差を解消する
def solve_2opt(tour: list[int], dist_matrix: list[list[float]]) -> list[int]:
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


# 3opt・3つの辺を交換するのを最大iterations回やる
def solve_3opt(
    tour: list[int],
    dist_matrix: list[list[float]],
    iterations: int = 100000,
) -> list[int]:
    tour = tour[:]
    improved = True
    iter = 0

    while improved and iter < iterations:
        improved = False
        for i in range(1, len(tour) - 3):
            for j in range(i + 1, len(tour) - 2):
                for k in range(j + 1, len(tour) - 1):
                    current_cost = total_distance(tour, dist_matrix)
                    iter += 1

                    P1 = tour[:i]
                    P2 = tour[i:j]
                    P3 = tour[j:k]
                    P4 = tour[k:]

                    patterns = [
                        P1 + P3 + P2 + P4,
                        P1 + list(reversed(P2)) + list(reversed(P3)) + P4,
                        P1 + P3 + list(reversed(P2)) + P4,
                        P1 + list(reversed(P3)) + P2 + P4,
                        P1 + list(reversed(P3)) + list(reversed(P2)) + P4,
                    ]

                    for pattern in patterns:
                        new_cost = total_distance(pattern, dist_matrix)
                        if new_cost < current_cost:
                            tour = pattern
                            improved = True
                            break

                if improved:
                    break
            if improved:
                break

    return tour


"""
アニーリングで使う近傍法の関数・or_opt,two_opt,three_opt
"""


# ランダムに、長さ1~3の1つの辺を取ってきて、どこかに挿入する
def or_opt(tour: list[int]) -> list[int]:
    n = len(tour)

    segment_length = random.randint(1, min(3, n - 1))
    i = random.randint(0, n - segment_length)
    j = i + segment_length
    segment = tour[i:j]
    rest = tour[:i] + tour[j:]

    insert_pos = random.randint(0, len(rest))
    new_tour = rest[:insert_pos] + segment + rest[insert_pos:]

    return new_tour


# ランダムに2本の辺を取ってきて交換する
def two_opt(tour: list[int]) -> list[int]:
    n = len(tour)
    while True:
        i, j = sorted(random.sample(range(n), 2))
        if j - i > 1:
            break
    new_tour = tour[:i] + list(reversed(tour[i : j + 1])) + tour[j + 1 :]
    return new_tour


# 3本の辺を取って組み替える。どのパターンを採用するかはランダム
def three_opt(tour: list[int]):
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

    pattern_random_index = random.randint(0, 4)
    new_tour = patterns[pattern_random_index]

    return new_tour


# 2opt,3opt,or_optを用いた焼きなまし法。局所解にはまったら温度をリセットする
# C++では10億回くらいは回せる
def solve_annealing(
    tour: list[int],
    dist_matrix: list[list[float]],
    initial_temp=None,
    final_temp=1e-9,
    alpha=0.9999999,
    max_iter=1e8,
) -> list[int]:
    # 2opt、3opt、or_optをある確率で選ぶ
    def neighbor(tour):
        p = random.random()
        if p < 0.3:
            new_tour = two_opt(tour)
        elif p < 0.65:
            new_tour = three_opt(tour)
        else:
            new_tour = or_opt(tour)
        return new_tour

    current_tour = tour[:]
    best_tour = tour[:]
    current_cost = total_distance(current_tour, dist_matrix)
    best_cost = current_cost

    if initial_temp is None:
        initial_temp = current_cost * 0.1

    temp = initial_temp
    iter = 0

    stagnation_counter = 0
    stag_check_before_cost = current_cost

    while final_temp < temp and iter < max_iter:
        # 焼きなましの主要部分------
        new_tour = neighbor(current_tour)
        new_cost = total_distance(new_tour, dist_matrix)

        delta = new_cost - current_cost

        if delta < 0 or math.exp(-delta / temp) > random.random():
            current_tour = new_tour[:]
            current_cost = new_cost

        temp *= alpha
        # ------------------------

        # デバッグ
        # 途中経過を見る
        if iter % 500000 == 0:
            print("iter = ", iter)
            print("temp= ", temp)
            print("score= ", current_cost)

        # ここでは500万回回しても距離が変わらなければ、局所解とみなして温度をリセット
        if abs(stag_check_before_cost - current_cost) < 0.01:
            stagnation_counter += 1
            if stagnation_counter > 5000000:
                print("Reset temp!")
                temp = initial_temp * 0.1
                print("new temp=", temp)
                stagnation_counter = 0

                # 局所解の中で一番いいルートを記録
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_tour = current_tour[:]
            stag_check_before_cost = current_cost

        else:
            stagnation_counter = 0
            stag_check_before_cost = current_cost

        iter += 1

    return best_tour


def write_tour(tour, filename):
    """ツアーを指定ファイルに書き込む（1行目:index, 2行目以降:都市番号）"""
    with open(filename, "w") as f:
        f.write(format_tour(tour) + "\n")


if __name__ == "__main__":
    assert len(sys.argv) > 2
    cities = read_input(sys.argv[1])
    dist_matrix = distance_matrix(cities)

    tour = solve_greedy_multi_start(dist_matrix, num_starts=2000)
    print("greedy = ", total_distance(tour, dist_matrix))

    cost = total_distance(tour, dist_matrix)

    # N = 128, input_4.csv用のパラメータ
    tour = solve_annealing(
        tour,
        dist_matrix,
        initial_temp=cost * 0.5,
        final_temp=1e-9,
        alpha=0.999997,
        max_iter=100000000,
    )

    # N = 512, input_5.csv or N = 2048, input_6.csv
    # tour = solve_annealing(tour, dist_matrix)
    print("annealing = ", total_distance(tour, dist_matrix))

    # あんまり意味ない？
    tour = solve_2opt(tour, dist_matrix)
    print("opt2 = ", total_distance(tour, dist_matrix))

    # tour = solve_3opt(tour, dist_matrix, iterations=100000)
    # print("opt3 = ", total_distance(tour, dist_matrix))

    write_tour(tour, sys.argv[2])
