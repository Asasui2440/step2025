# python hw2.py large.txt large_answer.txt
#  python3 score_checker.py large.txt large_answer.txt

# 問題
# 単語ファイル 例えばsmall.txtの列挙されたそれぞれの単語の最大のスコアを持つ
# アナグラムをoutputファイルに出力する。単語をすべて使う必要はない。


import sys
import time

# SCORES of the characters:
# ----------------------------------------
# | 1 point  | a, e, h, i, n, o, r, s, t |
# | 2 points | c, d, l, m, u             |
# | 3 points | b, f, g, p, v, w, y       |
# | 4 points | j, k, q, x, z             |
# ----------------------------------------


SCORES = [1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4]


class Dictionary:
    def __init__(self, word, word_vec, score):
        """
        クラスの初期化メソッド
        :param word: 単語 (str)
        :param word_vec: 単語のベクトル (tuple)
        :param score: 単語のスコア (int)
        """
        self.word = word  # 単語
        self.word_vec = word_vec  # 単語のベクトル
        self.score = score  # 単語のスコア


# スコアの計算
def score(word_vec: tuple) -> int:
    score = 0
    for i in range(len(word_vec)):
        score += word_vec[i] * SCORES[i]  # 文字の出現回数 * その文字のスコア
    return score


# 26個の要素を持つ配列(ベクトル)を用意。(26文字でサイズが固定できるので)
def to_vector(word: str) -> tuple:
    vec = [0] * 26
    for c in word:
        vec[ord(c) - ord("a")] += 1
    return tuple(
        vec
    )  # リストよりもtuple(組み合わせ)の方がメモリ使用量が少ないらしいので、tupleにして返す


def is_word_anagram(word_vec: tuple, word_dict_tuple: tuple) -> bool:
    # 単語ベクトルが辞書の単語ベクトルを包含しているかを確認

    for i in range(26):
        if word_vec[i] < word_dict_tuple.word_vec[i]:
            return False
    return True


# 引数の確認
if len(sys.argv) < 3:
    print("Usage: python hw2.py (input_file).txt (output_file).txt")
    sys.exit(1)


start = time.perf_counter()
with open("words.txt") as dictionary:
    dict_tuple = []
    for word in dictionary:
        word = word.strip()
        vec = to_vector(word)
        word_score = score(vec)
        dict_tuple.append(
            Dictionary(word, vec, word_score)
        )  # 単語、単語の出現回数ベクトルを保持

dict_tuple.sort(key=lambda x: -x.score)  # スコアが大きい順にソートする


input_file = sys.argv[1]
with open(input_file, "r") as f:
    anagram_word_list = []  # ここにanagramを保存していく
    for word in f:
        word = word.strip()
        vec = to_vector(word)
        # filterとnextを使用して条件を満たす最初の単語を取得。
        matching_word = next(
            filter(lambda word_dict: is_word_anagram(vec, word_dict), dict_tuple),
            None,  # 条件を満たす単語がない場合は None を返す
        )

        if matching_word:
            anagram_word_list.append(matching_word.word)


output_file = sys.argv[2]
with open(output_file, "w") as o:
    for row in anagram_word_list:  # anagram_word_listにある単語を書き込む
        o.write(row + "\n")


# 実行時間を計測  large.txtで0.02
end = time.perf_counter()
print("Runtimes: {:.2f}".format((end - start) / 60))
