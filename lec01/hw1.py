
# 問題：与えられた文字列のアナグラムを列挙する

# words.txtの辞書の単語をソートする。
sort_words_dict = []  # ここにソートした単語と、元の単語を追加していく
with open('words.txt') as dictionary:
    for word in dictionary:
        word = word.strip()
        sorted_word = ''.join(sorted(word))
        sort_words_dict.append((sorted_word,word)) # ソートした単語と、そのままの単語を持たせる

sort_words_dict.sort()  # これを、ソートした単語のアルファベット順にまたソートする


def anagram_algo(word,sort_words_dict): 
    word = ''.join(sorted(word))  # 入力された単語をソートする
    anagram_words = [] # アナグラムを保持するリスト
   
    # ２部探索
    left = 0
    right = len(sort_words_dict)
    index = -1
    while(left < right):
            middle = (left+right)//2
            if word < sort_words_dict[middle][0]:  
                right = middle
            elif word > sort_words_dict[middle][0]:
                left = middle + 1
            else: 
                 index = middle  # アナグラムが見つかったらループを抜ける
                 break

    if index != -1:
         for i in range (len(sort_words_dict)):  # ここでもう一度辞書のループを回す(非効率かも)
              # 見つかったアナグラムとソートした単語が等しい時、リストにその単語を追加していく
              if(sort_words_dict[i][0] == sort_words_dict[index][0]): 
                   anagram_words.append(sort_words_dict[i][1])
       
    return anagram_words   # アナグラムを保持したリストを返す
    
    
input_word = input('Input a word\n') # 1つの単語の入力を指示

anagram_words = anagram_algo(input_word,sort_words_dict)
if len(anagram_words)>0:
   print("anagrams: ")
   for anagram_word in anagram_words:
        print(anagram_word)
else:
     print("No anagrams")  # アナグラムが1つもない











 







