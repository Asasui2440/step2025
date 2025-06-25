import sys
from solver_opt import distance,solve_greedy,solve_opt2
from common import print_tour, read_input

def solve_lin_kernighan_approx(tour: list[int], cities: list[tuple[float,float]]) -> list[int]:
    """Lin-Kernighan近似アルゴリズム"""
    def gain(i, j, k, l):
        """2-opt交換のゲインを計算"""
        a, b = tour[i], tour[j]
        c, d = tour[k], tour[l]
        return (distance(cities[a], cities[b]) + distance(cities[c], cities[d]) -
                distance(cities[a], cities[c]) - distance(cities[b], cities[d]))
    
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
                tour[i:j+1] = reversed(tour[i:j+1])
                counter += 1
                if counter > improved_limit:
                     break
                improved = True
                break
    
    return tour


if __name__ == '__main__':
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    tour = solve_greedy(cities)
    tour = solve_opt2(tour,cities)
    tour = solve_lin_kernighan_approx(tour,cities)
    print_tour(tour)
