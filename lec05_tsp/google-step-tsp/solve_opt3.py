import sys
import random

from common import print_tour, read_input
from solver_opt import (
    distance_matrix,
    total_distance,
    solve_opt2,
    solve_greedy_multi_start,
)


def solve_3opt_limited(
    tour: list[int], dist_matrix: list[list[float]], window_size: int = 20
) -> list[int]:
    """制限付き3-opt最適化 - O(n * window_size²)"""
    improved = True
    improved_limit = 10000
    count = 0
    n = len(tour)

    while improved and count < improved_limit:
        improved = False

        # ランダムな開始点から制限された範囲で探索
        for start in range(0, n, window_size // 2):  # 重複を避けるため半分ずつずらす
            end = min(start + window_size, n)

            for i in range(start + 1, end - 4):
                for j in range(i + 2, end - 2):
                    for k in range(j + 2, min(end, n)):
                        # 3つの辺を削除して新しい経路を作成
                        a, b = tour[i - 1], tour[i]
                        c, d = tour[j - 1], tour[j]
                        e, f = tour[k - 1], tour[k]

                        # 元の距離
                        old_dist = (
                            dist_matrix[a][b] + dist_matrix[c][d] + dist_matrix[e][f]
                        )

                        # 新しい距離の候補
                        new_dist1 = (
                            dist_matrix[a][c] + dist_matrix[b][e] + dist_matrix[d][f]
                        )
                        new_dist2 = (
                            dist_matrix[a][d] + dist_matrix[c][e] + dist_matrix[b][f]
                        )
                        new_dist3 = (
                            dist_matrix[a][d] + dist_matrix[c][f] + dist_matrix[b][e]
                        )

                        min_new_dist = min(new_dist1, new_dist2, new_dist3)

                        if min_new_dist < old_dist:
                            # 最良の新しい経路を適用
                            if min_new_dist == new_dist1:
                                tour[i:j] = reversed(tour[i:j])
                                tour[j:k] = reversed(tour[j:k])
                            elif min_new_dist == new_dist2:
                                tour[i:j] = reversed(tour[i:j])
                            else:  # new_dist3
                                tour[j:k] = reversed(tour[j:k])

                            count += 1
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return tour


def solve_3opt_random(
    tour: list[int],
    dist_matrix: list[list[float]],
    iterations: int = 50000,
) -> list[int]:
    """ランダム3-opt最適化 - O(iterations)"""
    n = len(tour)
    best_tour = tour[:]
    best_cost = total_distance(tour, dist_matrix)

    for _ in range(iterations):
        # ランダムに3つの都市を選ぶ
        while True:
            a, b, c = sorted(random.sample(range(n), 3))
            if b - a > 1 and c - b > 1:  # 適切な間隔を保つ
                break

        # 3つのセグメントに分割
        P1 = tour[:a]
        P2 = tour[a:b]
        P3 = tour[b:c]
        P4 = tour[c:]

        # 可能なパターンを試す
        patterns = [
            P1 + P3 + P2 + P4,
            P1 + list(reversed(P2)) + list(reversed(P3)) + P4,
            P1 + P3 + list(reversed(P2)) + P4,
            P1 + list(reversed(P3)) + P2 + P4,
            P1 + list(reversed(P3)) + list(reversed(P2)) + P4,
        ]

        for pattern in patterns:
            new_cost = total_distance(pattern, dist_matrix)
            if new_cost < best_cost:
                best_tour = pattern[:]
                best_cost = new_cost

    return best_tour


def solve_3opt(tour: list[int], dist_matrix: list[list[float]]) -> list[int]:
    """3-opt最適化 - O(n³)"""
    improved = True
    improved_limit = 100
    count = 0
    while improved:
        improved = False
        n = len(tour)

        for i in range(1, n - 4):
            for j in range(i + 2, n - 2):
                for k in range(j + 2, n):
                    # 3つの辺を削除して新しい経路を作成
                    a, b = tour[i - 1], tour[i]
                    c, d = tour[j - 1], tour[j]
                    e, f = tour[k - 1], tour[k]

                    # 元の距離
                    old_dist = dist_matrix[a][b] + dist_matrix[c][d] + dist_matrix[e][f]

                    # 新しい距離の候補
                    new_dist1 = (
                        dist_matrix[a][c] + dist_matrix[b][e] + dist_matrix[d][f]
                    )
                    new_dist2 = (
                        dist_matrix[a][d] + dist_matrix[c][e] + dist_matrix[b][f]
                    )
                    new_dist3 = (
                        dist_matrix[a][d] + dist_matrix[c][f] + dist_matrix[b][e]
                    )

                    min_new_dist = min(new_dist1, new_dist2, new_dist3)

                    if min_new_dist < old_dist:
                        if count < improved_limit:
                            # 最良の新しい経路を適用
                            if min_new_dist == new_dist1:
                                tour[i:j] = reversed(tour[i:j])
                                tour[j:k] = reversed(tour[j:k])
                            elif min_new_dist == new_dist2:
                                tour[i:j] = reversed(tour[i:j])
                            else:  # new_dist3
                                tour[j:k] = reversed(tour[j:k])

                            count += 1
                            # if count % 500 == 0:
                            # print("count=", count)
                            if count > improved_limit:
                                break
                            improved = True
                            break
                if improved:
                    break
            if improved:
                break

    return tour


if __name__ == "__main__":
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    dist_matrix = distance_matrix(cities)
    tour = solve_greedy_multi_start(dist_matrix)
    tour = solve_opt2(tour, dist_matrix)
    # tour = solve_3opt(tour, dist_matrix)
    # tour = solve_3opt_limited(tour, dist_matrix)
    tour = solve_3opt_random(tour, dist_matrix)

    print_tour(tour)
