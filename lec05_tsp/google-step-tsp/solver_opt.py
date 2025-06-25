#!/usr/bin/env python3

import sys
import math
import random

from common import print_tour, read_input



def distance(city1:tuple[float,float], city2:tuple[float,float]) -> float:
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

def total_distance(tour:list[int],cities:list[tuple[float,float]])-> float:
    total_dist = sum(distance(cities[tour[i]],cities[tour[i+1]]) for i in range(len(tour)-1))
    total_dist += distance(cities[tour[-1]],cities[tour[0]])
    return total_dist

def solve_opt2(tour:list[int],cities:list[tuple[float,float]])-> list[int]:
    improved = True
    while improved:
        improved = False
        for i in range(1,len(tour) - 2):
            for j in range(i+1,len(tour)-1):
                a,b = tour[i-1],tour[i]
                c,d = tour[j],tour[j+1]
                if (distance(cities[a],cities[b]) + distance(cities[c],cities[d]) 
                > distance(cities[a],cities[c]) + distance(cities[b],cities[d])):
                    tour[i:j+1] = reversed(tour[i:j+1])
                    improved = True

    return tour

def or_opt(tour:list[int]):
    n = len(tour)
    segment_length = random.randint(1,min(3,n)) # 最大で全部の都市
    i = random.randint(0,n - segment_length) 
    j =  i + segment_length
    if n <= 3:
        return tour[:]
    segment = tour[i:j]
    rest = tour[:i] + tour[j:]

    insert_pos = random.randint(1,len(rest)-1)
    new_tour = rest[:insert_pos] + segment + rest[insert_pos:]
    return new_tour

def two_opt(tour:list[int])-> list[int]:
    # jの方が大きくなるように取る
    while True:
        i,j = sorted(random.sample(range(len(tour)),2))
        if j - i > 1:
            break
    new_tour = tour[:i] + list(reversed(tour[i:j+1])) + tour[j+1:]
    return new_tour


def three_opt(tour:list[int]):
    n = len(tour)
    while True:
        a,b,c = sorted(random.sample(range(n),3))
        if not (a == b or b == c):
            break
    P1 = tour[:a]
    P2 = tour[a:b]
    P3 = tour[b:c]
    P4 = tour[c:]

    patterns = [
        P1+P3 + P2 + P4,
        P1 + list(reversed(P2)) + list(reversed(P3)) + P4,
        P1 + P3 + list(reversed(P2)) + P4,
        P1 + list(reversed(P3)) + P2 + P4,
        P1 + list(reversed(P3)) + list(reversed(P2)) + P4
    ]

    new_tour = random.choice(patterns)
    return new_tour


def solve_multi_neighbors(cities:list[tuple[float,float]],initial_temp=1e6,final_temp=1e-4,alpha=0.995,max_iter=int(1e6)) -> list[int]:
    def neighbor(tour):
        p = random.random()
        if p < 0.4:
            return two_opt(tour)  
        elif p < 0.8:
            return three_opt(tour)
        else:
            return or_opt(tour)

    def cost(tour):
        return total_distance(tour,cities)


    tour = solve_greedy(cities)
    tour = solve_opt2(tour,cities)
    
    current = tour[:]
    best = tour[:]
    current_cost = cost(current)
    best_cost = cost(current)

    t = initial_temp

    for _ in range(max_iter):
        suggested_route = neighbor(current) # 経路の候補

        # suggested_routeの方が短かったら大体採用する
        d = cost(suggested_route) - current_cost
        if d <= 0 or random.random() < math.exp(-d/t):
            current = suggested_route
            current_cost = cost(current)
            if current_cost < best_cost:
                best = current
                best_cost = current_cost
        t *= alpha

        if t < final_temp:
            break

    return best

                

def solve_annealing(tour:list[int],cities:list[tuple[float,float]],initial_temp=1e6,final_temp=1e-4,alpha=0.999,max_iter=int(1e6)) -> list[int]:
    current_tour = tour[:] 
    best_tour = tour[:]
    current_cost = total_distance(current_tour,cities)
    best_cost = current_cost
    temp = initial_temp


    for iter in range(max_iter):
        i,j = sorted(random.sample(range(len(tour)),2))
        new_tour = current_tour[:i] + list(reversed(current_tour[i:j+1])) + current_tour[j+1:]
        new_cost = total_distance(new_tour,cities)

        delta = new_cost - current_cost

        if delta < 0 or math.exp(-delta/temp) > random.random():
            #print(f"iter: {iter}, temp: {temp}, delta: {delta}")
            current_tour = new_tour
            current_cost = new_cost
            if current_cost < best_cost:
                best_tour = current_tour
                best_cost = current_cost
        

        temp *= alpha
        if temp < final_temp:
            break

    return best_tour

def solve_greedy(cities:list[tuple[float,float]]) -> list[int]:
    N = len(cities)

    dist = [[0.0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])

    current_city = 0
    unvisited_cities = set(range(1, N))
    tour = [current_city]

    while unvisited_cities:
        next_city = min(unvisited_cities,
                        key=lambda city: dist[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    return tour


def solve_annealing_opt2(cities:list[tuple[float,float]]) -> list[int]:
    tour = solve_greedy(cities)
    tour = solve_annealing(tour,cities)
    tour = solve_opt2(tour,cities)
    return tour


def solve_3opt(tour: list[int], cities: list[tuple[float,float]]) -> list[int]:
    """3-opt最適化"""
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
                    a, b = tour[i-1], tour[i]
                    c, d = tour[j-1], tour[j]
                    e, f = tour[k-1], tour[k]
                    
                    # 元の距離
                    old_dist = (distance(cities[a], cities[b]) + 
                               distance(cities[c], cities[d]) + 
                               distance(cities[e], cities[f]))
                    
                    # 新しい距離の候補
                    new_dist1 = (distance(cities[a], cities[c]) + 
                                distance(cities[b], cities[e]) + 
                                distance(cities[d], cities[f]))
                    new_dist2 = (distance(cities[a], cities[d]) + 
                                distance(cities[c], cities[e]) + 
                                distance(cities[b], cities[f]))
                    new_dist3 = (distance(cities[a], cities[d]) + 
                                distance(cities[c], cities[f]) + 
                                distance(cities[b], cities[e]))
                    
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
                            if count > improved_limit:
                                break
                            improved = True
                            break
                if improved:
                    break
            if improved:
                break
    
    return tour



if __name__ == '__main__':
    assert len(sys.argv) > 1
    cities = read_input(sys.argv[1])
    #tour = solve_greedy(cities)
    #tour = solve_opt2(tour,cities)
    #tour = solve_3opt(tour,cities)
    tour = solve_annealing_opt2(cities)
    # tour = solve_multi_neighbors(cities)
    print_tour(tour)
