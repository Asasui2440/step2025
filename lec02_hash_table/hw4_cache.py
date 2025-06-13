from __future__ import annotations
from typing import Optional
# from hw1_hash_table import put

# Implement a data structure that stores the most recently accessed N pages.
# See the below test cases to see how it should work.
#
# Note: Please do not use a library like collections.OrderedDict). The goal is
#       to implement the data structure yourself!


class Page:
    def __init__(
        self: Page,
        url: str,
        contents: str,
        prev: Optional[Page] = None,
        next: Optional[Page] = None,
    ):
        self.url = url
        self.contents = contents
        self.prev = prev
        self.next = next

    # これは確認用
    def __str__(self):
        next_url = self.next.url if self.next else "None"
        return f"Page(url={self.url}, contents={self.contents}, next={next_url})"

    def __repr__(self):
        return self.__str__()


class Cache:
    # Initialize the cache.
    # |n|: The size of the cache.、
    def __init__(self: Cache, n: int):
        self.head = None  # 先頭のポインタ
        self.tail = None  # 末尾のポインタ
        self.cache_size = n
        self.size = 0
        self.hash_table = {}

    # Access a page and update the cache so that it stores the most recently
    # accessed N pages. This needs to be done with mostly O(1).
    # |url|: The accessed URL
    # |contents|: The contents of the URL
    def access_page(self: Cache, url: str, contents: str) -> None:
        # ------------------------#
        if (url, contents) in self.hash_table:
            page = self.hash_table[(url, contents)]
            if page is self.head:  # 先頭のページだったらそのまま返す
                return

            # ページを一旦削除
            if page.prev:
                page.prev.next = page.next
            if page.next:
                page.next.prev = page.prev
            if page is self.tail:
                self.tail = page.prev

            # ページを先頭に持ってくる
            page.next = self.head
            page.prev = None
            if self.head:
                self.head.prev = page
            self.head = page

        else:
            # keyがハッシュテーブルになければ新たに作る
            page = Page(url, contents, None, None)
            self.hash_table[(url, contents)] = page
            if self.head is None:
                self.head = page
            else:
                page.next = self.head
                page.prev = None
                self.head.prev = page
                self.head = page

            if self.tail is None:
                self.tail = page

            self.size += 1

        if self.size > self.cache_size:
            del self.hash_table[(self.tail.url, self.tail.contents)]
            if self.tail.prev:
                self.tail.prev.next = None
            self.tail = self.tail.prev
            self.size -= 1

        # ------------------------#

    # Return the URLs stored in the cache. The URLs are ordered in the order
    # in which the URLs are mostly recently accessed.
    def get_pages(self: Cache) -> list:
        # ------------------------#
        pages = []
        pointer = self.head

        while pointer:
            pages.append(pointer.url)
            pointer = pointer.next
        # ------------------------#
        # print(pages)
        return pages


def cache_test():
    # Set the size of the cache to 4.
    cache = Cache(4)

    # Initially, no page is cached.
    assert cache.get_pages() == []
    # Access "a.com".
    cache.access_page("a.com", "AAA")
    # "a.com" is cached.
    assert cache.get_pages() == ["a.com"]

    # Access "b.com".
    cache.access_page("b.com", "BBB")
    # The cache is updated to:
    #   (most recently accessed)<-- "b.com", "a.com" -->(least recently accessed)
    assert cache.get_pages() == ["b.com", "a.com"]

    # Access "c.com".
    cache.access_page("c.com", "CCC")
    # The cache is updated to:
    #   (most recently accessed)<-- "c.com", "b.com", "a.com" -->(least recently accessed)
    assert cache.get_pages() == ["c.com", "b.com", "a.com"]

    # Access "d.com".
    cache.access_page("d.com", "DDD")
    # The cache is updated to:
    #   (most recently accessed)<-- "d.com", "c.com", "b.com", "a.com" -->(least recently accessed)
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    # Access "d.com" again.
    cache.access_page("d.com", "DDD")
    # The cache is updated to:
    #   (most recently accessed)<-- "d.com", "c.com", "b.com", "a.com" -->(least recently accessed)
    # print(cache.get_pages())
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    # Access "a.com" again.
    cache.access_page("a.com", "AAA")
    # The cache is updated to:
    #   (most recently accessed)<-- "a.com", "d.com", "c.com", "b.com" -->(least recently accessed)
    assert cache.get_pages() == ["a.com", "d.com", "c.com", "b.com"]

    cache.access_page("c.com", "CCC")
    assert cache.get_pages() == ["c.com", "a.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]

    # Access "e.com".
    cache.access_page("e.com", "EEE")
    # The cache is full, so we need to remove the least recently accessed page "b.com".
    # The cache is updated to:
    #   (most recently accessed)<-- "e.com", "a.com", "c.com", "d.com" -->(least recently accessed)
    # print(cache.get_pages())
    assert cache.get_pages() == ["e.com", "a.com", "c.com", "d.com"]

    # Access "f.com".
    cache.access_page("f.com", "FFF")
    # The cache is full, so we need to remove the least recently accessed page "c.com".
    # The cache is updated to:
    #   (most recently accessed)<-- "f.com", "e.com", "a.com", "c.com" -->(least recently accessed)
    assert cache.get_pages() == ["f.com", "e.com", "a.com", "c.com"]

    # Access "e.com".
    cache.access_page("e.com", "EEE")
    # The cache is updated to:
    #   (most recently accessed)<-- "e.com", "f.com", "a.com", "c.com" -->(least recently accessed)
    assert cache.get_pages() == ["e.com", "f.com", "a.com", "c.com"]

    # Access "a.com".
    cache.access_page("a.com", "AAA")
    # The cache is updated to:
    #   (most recently accessed)<-- "a.com", "e.com", "f.com", "c.com" -->(least recently accessed)
    assert cache.get_pages() == ["a.com", "e.com", "f.com", "c.com"]

    # set the cache size 1
    cache = Cache(1)
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com"]

    # over the cache size
    cache.access_page("b.com", "BBB")
    assert cache.get_pages() == ["b.com"]

    print("Tests passed!")


if __name__ == "__main__":
    cache_test()


# urlによってページが違うものがあった場合は？
# urlに対して、ポインタを持っておくor 双方向リストで考える。
# url ポインタ prev_page
