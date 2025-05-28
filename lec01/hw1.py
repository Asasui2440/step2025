# 問題：与えられた文字列のアナグラムを列挙する

# words.txtの辞書の単語をソートする。
sort_words_dict = []  # ここにソートした単語と、元の単語を追加していく
with open("words.txt") as dictionary:
    for word in dictionary:
        word = word.strip()
        sorted_word = "".join(sorted(word))
        sort_words_dict.append(
            (sorted_word, word)
        )  # ソートした単語と、そのままの単語を持たせる

sort_words_dict.sort()  # これを、ソートした単語のアルファベット順にまたソートする


def anagram_algo(word: str, sort_words_dict: list) -> list:
    sorted_given_word = "".join(sorted(word))  # 入力された単語をソートする
    anagram_words = []  # アナグラムを保持するリスト

    """
    ２部探索
    sort_words_dict[left][0] < sorted(given_word) <= sort_words_dict[right][0] を保ちながら right - left を小さくしていく
    最終的に、sort_words_dict[left][0] < sorted(given_word) <= sort_words_dict[left + 1][0]になる。
    right = left+1が、該当する区間の開始地点になる。
    """
    left = 0
    right = len(sort_words_dict) - 1

    # 指定されたものが範囲外になった場合
    if (
        sort_words_dict[right][0] < sorted_given_word
        or sort_words_dict[left][0] > sorted_given_word
    ):
        return []

    while right != left + 1:
        middle = (left + right) // 2
        if sorted_given_word <= sort_words_dict[middle][0]:
            right = middle
        elif sorted_given_word > sort_words_dict[middle][0]:
            left = middle

        if sort_words_dict[0][0] == sorted_given_word:
            index = 0
        else:
            index = right
    # 開始地点のindexから、ソートした単語が一致しているところまでindexを増やしていく
    while (
        index < len(sort_words_dict) and sort_words_dict[index][0] == sorted_given_word
    ):
        anagram_words.append(sort_words_dict[index][1])
        index += 1  # 次の単語を確認

    return anagram_words  # アナグラムを保持したリストを返す


input_word = input("Input a word\n")  # 1つの単語の入力を指示

anagram_words = anagram_algo(input_word, sort_words_dict)
if len(anagram_words) > 0:
    print("anagrams: ")
    for anagram_word in anagram_words:
        print(anagram_word)
else:
    print("No anagrams")  # アナグラムが1つもない
