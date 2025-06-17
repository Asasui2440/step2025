# python wikipedia_graph.py wikipedia_dataset/pages_small.txt wikipedia_dataset/links_small.txt
# python wikipedia_graph.py wikipedia_dataset/pages_medium.txt wikipedia_dataset/links_medium.txt
# python wikipedia_graph.py wikipedia_dataset/pages_large.txt wikipedia_dataset/links_large.txt

import sys
import collections


class Wikipedia:
    # Initialize the graph of pages.
    def __init__(self, pages_file, links_file):
        # A mapping from a page ID (integer) to the page title.
        # For example, self.titles[1234] returns the title of the page whose
        # ID is 1234.
        self.titles = {}

        # A set of page links.
        # For example, self.links[1234] returns an array of page IDs linked
        # from the page whose ID is 1234.
        self.links = {}

        # Read the pages file into self.titles.
        with open(pages_file) as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                assert id not in self.titles, id
                self.titles[id] = title
                self.links[id] = []
        print("Finished reading %s" % pages_file)

        # Read the links file into self.links.
        with open(links_file) as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                assert src in self.titles, src
                assert dst in self.titles, dst
                self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()

    # Example: Find the longest titles.
    def find_longest_titles(self):
        titles = sorted(self.titles.values(), key=len, reverse=True)
        print("The longest titles are:")
        count = 0
        index = 0
        while count < 15 and index < len(titles):
            if titles[index].find("_") == -1:
                print(titles[index])
                count += 1
            index += 1
        print()

    # Example: Find the most linked pages.
    def find_most_linked_pages(self):
        link_count = {}
        for id in self.titles.keys():
            link_count[id] = 0

        for id in self.titles.keys():
            for dst in self.links[id]:
                link_count[dst] += 1

        print("The most linked pages are:")
        link_count_max = max(link_count.values())
        for dst in link_count.keys():
            if link_count[dst] == link_count_max:
                print(self.titles[dst], link_count_max)
        print()

    # Homework #1: Find the shortest path.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.

    # titleからidを見つける
    def find_id(self, start, goal):
        for id, title in self.titles.items():
            if title == start:
                start_id = id
            if title == goal:
                goal_id = id

        if start_id is None or goal_id is None:
            print("Start or goal page not found")
            return
        else:
            return start_id, goal_id

    def find_shortest_path(self, start, goal):
        # ------------------------#
        start_id, goal_id = self.find_id(start, goal)

        # bfs
        queue = collections.deque()
        visited = {}
        previous = {}

        queue.append(start_id)
        visited[start_id] = True
        previous[start_id] = None
        while len(queue):
            node = queue.popleft()
            if node == goal_id:
                break
            for child in self.links[node]:
                if child not in visited:
                    queue.append(child)
                    visited[child] = True
                    previous[child] = node

        if goal_id in previous:
            path = []
            current = goal_id
            while current is not None:
                path.append(self.titles[current])
                current = previous[current]
            path.reverse()
            print("->".join(path))
        else:
            print("Not found.")

        # ------------------------#

    # Homework #2: Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        # ------------------------#
        old_page_rank = {}
        new_page_rank = {}

        # 初期値の設定
        for id in self.titles.keys():
            old_page_rank[id] = 1.0
            new_page_rank[id] = 0.0

        loop = 0
        diff = 1.0

        while diff > 0.01 and loop < 35:
            loop += 1
            diff = 0
            isolation_sum = 0

            # 全てが全てに15%与えるので結局0.15はみんな受け取る
            for id in self.titles.keys():
                new_page_rank[id] = 0.15

            for id in self.titles.keys():
                # 85%をリンク先のノードに与える
                if len(self.links[id]) > 0:
                    for dst in self.links[id]:
                        new_page_rank[dst] += (
                            old_page_rank[id] * 0.85 / len(self.links[id])
                        )
                # どこにもリンクされていない時、残りの85%を全てに分配。isolation_sumに貯めておく。
                else:
                    isolation_sum += old_page_rank[id] * 0.85

            isolation_sum = isolation_sum / len(self.titles)

            for id in self.titles.keys():
                new_page_rank[id] += isolation_sum

            # diffの計算
            diff = sum(
                (new_page_rank[id] - old_page_rank[id]) ** 2
                for id in self.titles.keys()
            )
            old_page_rank = new_page_rank.copy()
            print(diff)

            # 確認用
            if loop % 5 == 0:
                print("loop: ", loop)
                total = 0
                for id in self.titles.keys():
                    total += new_page_rank[id]
                # 合計がノードの数になっているか
                print("gap ", abs(total - len(self.titles)))

        # 上位のページを出力
        sorted_pages = sorted(new_page_rank.items(), key=lambda x: x[1], reverse=True)
        print("The most popular pages are:")
        index = min(10, len(self.titles))
        for id, rank in sorted_pages[:index]:
            print(f"{self.titles[id]}: {rank:.4f}")

        # ------------------------#

    # Homework #3 (optional):
    # Search the longest path with heuristics.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_longest_path(self, start, goal):
        # ------------------------#
        # 双方向bfsで、被らないように経路を探索していき、n回目にノードが被った時点でbreakする。
        # prev_goalmeeting_node]でkeyerrorしてしまったし、動いてもパスの長さ6とかしかない

        previous = {}
        prev_goal = {}
        visited = {}
        visited_goal = {}

        start_id, goal_id = self.find_id(start, goal)
        if start_id == goal_id:
            print([self.titles[start_id]])
            return

        # 双方向探索のためのキュー
        queue_start = collections.deque()
        queue_goal = collections.deque()

        queue_start.append(start_id)
        queue_goal.append(goal_id)

        visited[start_id] = True
        visited_goal[goal_id] = True

        previous[start_id] = None
        prev_goal[goal_id] = None

        meeting_node = None
        cnt = 0

        while queue_start and queue_goal:
            # Start側の探索
            node = queue_start.popleft()
            for child in self.links.get(node, []):
                if child in visited_goal:
                    cnt += 1
                    if cnt == 1000:
                        meeting_node = child
                        break
                elif child not in visited:
                    visited[child] = True
                    previous[child] = node
                    queue_start.append(child)
            if meeting_node:
                break

            # Goal側の探索
            node_goal = queue_goal.popleft()
            for child in self.links.get(node_goal, []):
                if child in visited:
                    cnt += 1
                    if cnt == 1000:
                        meeting_node = child
                        break
                elif child not in visited_goal:
                    visited_goal[child] = True
                    prev_goal[child] = node_goal
                    queue_goal.append(child)

            if meeting_node:
                break

        if meeting_node is None:
            print("Not found")
            return

        # 経路の復元
        path_from_start = []
        node = meeting_node
        path_from_goal = []

        while node is not None:
            path_from_start.append(self.titles[node])
            node = previous[node]
        path_from_start.reverse()

        node = prev_goal[meeting_node]
        while node is not None:
            path_from_goal.append(self.titles[node])
            node = prev_goal[node]
        full_path = path_from_start + path_from_goal

        if len(full_path) < 100:
            print(full_path)
        else:
            print(len(full_path))
        # ------------------------#

    # Helper function for Homework #3:
    # Please use this function to check if the found path is well formed.
    # 'path': An array of page IDs that stores the found path.
    #     path[0] is the start page. path[-1] is the goal page.
    #     path[0] -> path[1] -> ... -> path[-1] is the path from the start
    #     page to the goal page.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def assert_path(self, path, start, goal):
        assert start != goal
        assert len(path) >= 2
        assert self.titles[path[0]] == start
        assert self.titles[path[-1]] == goal
        for i in range(len(path) - 1):
            assert path[i + 1] in self.links[path[i]]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    # Example
    # wikipedia.find_longest_titles()
    # Example
    # wikipedia.find_most_linked_pages()
    # Homework #1
    # wikipedia.find_shortest_path("渋谷", "パレートの法則")
    # Homework #2
    # wikipedia.find_most_popular_pages()
    # Homework #3 (optional)
    wikipedia.find_longest_path("渋谷", "池袋")
    # wikipedia.find_longest_path("A", "F")
