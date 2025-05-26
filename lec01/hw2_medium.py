# python hw2_medium.py medium.txt
#  python3 score_checker.py medium.txt medium_answer.txt

import sys

# SCORES of the characters:
# ----------------------------------------
# | 1 point  | a, e, h, i, n, o, r, s, t |
# | 2 points | c, d, l, m, u             |
# | 3 points | b, f, g, p, v, w, y       |
# | 4 points | j, k, q, x, z             |
# ----------------------------------------


SCORES = [1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4]


def score(word):
    score = 0
    for c in word:
        if 'a' <= c <= 'z':
            score += SCORES[ord(c) - ord('a')]

    return score

def to_vector(word):
    vec = [0]*26
    for c in word:
        if 'a' <= c <= 'z':
            vec[ord(c) - ord('a')] += 1
    return tuple(vec)



if len(sys.argv) < 2:
    print("Usage: python hw2.py large.txt")
    sys.exit(1)


with open('words.txt') as dictionary:
    dict_vec = []
    for word in dictionary:
        word = word.strip()
        vec = to_vector(word)
        dict_vec.append((word,vec))

dict_vec.sort(key=lambda x: -score(x[0]))

input_file = sys.argv[1]
with open(input_file,'r') as f:
    anagram_word_list = []
    for word in f:
        word = word.strip()
        vec = to_vector(word)
        max_score = 0
        for word_dict,dict_word_vec in dict_vec:
            if all(vec[i] >= dict_word_vec[i] for i in range(26)):
                    max_score = score(word_dict)
                    max_word = word_dict
                    anagram_word_list.append(max_word)
                    break
           
  
             
with open('medium_answer.txt','w') as o:
    for row in anagram_word_list:
        o.write(row + '\n')

        
    
    
