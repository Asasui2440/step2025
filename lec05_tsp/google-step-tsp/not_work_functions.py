import sys
import math
import random


# 単純な貪欲
def solve_greedy(dist_matrix: list[list[float]]) -> list[int]:
    N = len(dist_matrix)
    current_city = 0
    unvisited_cities = set(range(1, N))
    tour = [current_city]

    while unvisited_cities:
        next_city = min(
            unvisited_cities, key=lambda city: dist_matrix[current_city][city]
        )
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    return tour


# 2optのアニーリング
def solve_annealing(
    tour: list[int],
    dist_matrix: list[list[float]],
    initial_temp=None,
    final_temp=1e-4,
    alpha=0.95,
    max_iter=int(100),
) -> list[int]:
    current_tour = tour[:]
    best_tour = tour[:]
    current_cost = total_distance(current_tour, dist_matrix)
    best_cost = current_cost

    if initial_temp is None:
        initial_temp = current_cost * 0.1

    temp = initial_temp

    for iter in range(max_iter):
        i, j = sorted(random.sample(range(len(tour)), 2))
        new_tour = (
            current_tour[:i]
            + list(reversed(current_tour[i : j + 1]))
            + current_tour[j + 1 :]
        )
        new_cost = total_distance(new_tour, dist_matrix)

        delta = new_cost - current_cost

        if delta < 0 or math.exp(-delta / temp) > random.random():
            # if delta < -300:
            #     print(f"iter: {iter}, temp: {temp}, delta: {delta}")
            current_tour = new_tour[:]
            current_cost = new_cost
            if current_cost < best_cost:
                best_tour = current_tour[:]
                best_cost = current_cost

        temp *= alpha
        if temp < final_temp:
            break

    return best_tour


# 近傍法
def solve_multi_neighbors(
    dist_matrix: list[list[float]],
    initial_temp=1e4,
    final_temp=1e-4,
    alpha=0.95,
    max_iter=int(1e6),
) -> list[int]:
    def neighbor(tour):
        p = random.random()
        if p < 0.4:
            return two_opt(tour, dist_matrix)
        elif p < 0.8:
            return three_opt(tour, dist_matrix)
        else:
            return or_opt(tour, dist_matrix)

    def cost(tour):
        return total_distance(tour, dist_matrix)

    tour = solve_greedy(dist_matrix)
    tour = solve_opt2(tour, dist_matrix)

    current = tour[:]
    best_tour = tour[:]
    current_cost = cost(current)
    best_cost = cost(current)

    t = initial_temp

    for _ in range(max_iter):
        suggested_route = neighbor(current)  # 経路の候補

        # suggested_routeの方が短かったら大体採用する
        d = cost(suggested_route) - current_cost
        if d <= 0 or random.random() < math.exp(-d / t):
            current = suggested_route
            current_cost = cost(current)
            if current_cost < best_cost:
                best_tour = current[:]
                best_cost = current_cost
        t *= alpha

        if t < final_temp:
            break

    return best_tour


# ランダムに1つの辺を取ってきて、どこかに挿入する
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


# 2optを10回のみ試す
def two_opt(tour: list[int], dist_matrix: list[list[float]]) -> list[int]:
    best_tour = tour[:]
    best_cost = total_distance(tour, dist_matrix)
    n = len(tour)

    for _ in range(10):
        i, j = sorted(random.sample(range(n), 2))
        if j - i <= 1:
            continue
        new_tour = tour[:i] + list(reversed(tour[i : j + 1])) + tour[j + 1 :]
        new_cost = total_distance(new_tour, dist_matrix)

        if new_cost < best_cost:
            best_tour = new_tour[:]
            best_cost = new_cost

    return best_tour


# 3optを1回だけ試す
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


# 開始地点からの最良の辺を求める？
def solve_lin_kernighan_approx(
    tour: list[int], dist_matrix: list[list[float]]
) -> list[int]:
    """Lin-Kernighan近似アルゴリズム"""

    def gain(i, j, k, l):
        """2-opt交換のゲインを計算"""
        a, b = tour[i], tour[j]
        c, d = tour[k], tour[l]
        # ゲイン = 削除するエッジのコスト - 追加するエッジのコスト
        old_cost = dist_matrix[a][b] + dist_matrix[c][d]
        new_cost = dist_matrix[a][c] + dist_matrix[b][d]
        return old_cost - new_cost  # 正のゲインが改善を意味する

    n = len(tour)
    improved = True
    improved_limit = 50
    counter = 0

    while improved:
        improved = False

        for start in range(n):
            # 開始点から最良の2-opt交換を探す
            best_gain = 0
            best_move = None

            for i in range(n):
                if i == start:
                    continue
                for j in range(i + 1, n):
                    if j == start:
                        continue

                    # 2-opt交換のゲインを計算
                    g = gain(start, (start + 1) % n, i, j)
                    if g > best_gain:
                        best_gain = g
                        best_move = (i, j)

            # 最良の交換を実行
            if best_move:
                i, j = best_move
                tour[i : j + 1] = reversed(tour[i : j + 1])
                counter += 1
                if counter > improved_limit:
                    break
                improved = True
                break

    return tour
