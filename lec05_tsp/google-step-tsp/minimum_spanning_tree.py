from collections import deque
import heapq
import sys
from common import read_input
from solver_opt import total_distance, distance_matrix, write_tour


def weighted_mst_prim(dist_matrix: list[list[float]]) -> list[tuple[float, int]]:
    """
    Prim法で重み付きMSTを構築する
    引数:
        dist_matrix: 距離行列 (N×N)
    戻り値:
        mst_edges: MSTの辺集合 [(親, 子), ...]
    """
    N = len(dist_matrix)
    used = [False] * N
    mincost = [float("inf")] * N
    prev = [-1] * N
    mincost[0] = 0
    hq = [
        (0.0, 0)
    ]  # (コスト, 頂点) priority queue：最初の要素が昇順に並ぶ。最小値の取り出しがO(logN)でできる
    mst_edges = []

    while hq:
        cost_u, u = heapq.heappop(hq)
        if used[u]:
            continue
        used[u] = True
        if prev[u] != -1:
            mst_edges.append((prev[u], u))
        for v in range(N):
            # v が未訪問の都市で、uからvへの距離が今までの最小より小さい時
            if not used[v] and dist_matrix[u][v] < mincost[v]:
                mincost[v] = dist_matrix[u][v]
                prev[v] = u
                heapq.heappush(hq, (dist_matrix[u][v], v))  # vをヒープに追加
    return mst_edges


def mst_edges_to_tour(mst_edges: list[tuple[float, int]], N: int) -> list[int]:
    """
    MSTの辺集合から巡回路（tour）を生成する（DFS順）
    引数:
        mst_edges: [(親, 子), ...]
        N: 都市数
    戻り値:
        tour: 都市の順列リスト
    """
    from collections import defaultdict

    # 隣接リストを作成
    adj = defaultdict(list)
    for u, v in mst_edges:
        adj[u].append(v)
        adj[v].append(u)

    tour = []
    visited = [False] * N

    def dfs(u):
        visited[u] = True
        tour.append(u)
        for v in adj[u]:
            if not visited[v]:
                dfs(v)

    dfs(0)  # 0番からスタート
    return tour


if __name__ == "__main__":
    assert len(sys.argv) > 2
    cities = read_input(sys.argv[1])
    dist_matrix = distance_matrix(cities)
    mst_edges = weighted_mst_prim(dist_matrix)
    tour = mst_edges_to_tour(mst_edges, len(cities))

    print("mst=", total_distance(tour, dist_matrix))
    write_tour(tour, sys.argv[2])
