import random
import time
import math
import sys

from common import print_tour, read_input
from solver_opt import total_distance,solve_greedy,solve_opt2,two_opt,three_opt,or_opt
from lin_kernighan import solve_lin_kernighan_approx




def solve_improved_annealing(cities: list[tuple[float,float]], time_limit=30) -> list[int]:
    """改善された焼きなまし法"""
    def neighbor(tour):
        p = random.random()
        if p < 0.4:
            return two_opt(tour)
        elif p < 0.7:
            return three_opt(tour)
        elif p < 0.9:
            return or_opt(tour)
        else:
            # より大きな変更
            return solve_lin_kernighan_approx(tour[:], cities)
    
    def cost(tour):
        return total_distance(tour, cities)
    
    # 複数の初期解から開始
    initial_tours = []
    for _ in range(5):
        tour = solve_greedy(cities)
        tour = solve_opt2(tour, cities)
        initial_tours.append(tour)
    
    best_tour = min(initial_tours, key=cost)
    best_cost = cost(best_tour)
    
    start_time = time.time()
    
    for initial_tour in initial_tours:
        if time.time() - start_time > time_limit:
            break
            
        current = initial_tour[:]
        current_cost = cost(current)
        
        # 適応的な温度パラメータ
        initial_temp = current_cost * 0.1
        final_temp = 1e-6
        alpha = 0.9995
        
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


if __name__ == '__main__':
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    tour = solve_improved_annealing(cities)
    print_tour(tour)

