#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <cctype>

using namespace std;

const int SCORES[26] = {1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4};

// 単語と文字カウントを保持する構造体
struct WordHash {
    string word;
    unordered_map<char, int> char_count;
};

// 文字カウントを計算
unordered_map<char, int> count_characters(const string &word) {
    unordered_map<char, int> char_count;
    for (char c : word) {
        if (isalpha(c)) {
            char_count[tolower(c)]++;
        }
    }
    return char_count;
}

// アナグラムかどうかを判定
bool is_anagram(const unordered_map<char, int> &input_count, const unordered_map<char, int> &word_count) {
    for (const auto &entry : word_count) {
        if (input_count.at(entry.first) < entry.second) {
            return false;
        }
    }
    return true;
}

// スコアを計算
int calculate_score(const unordered_map<char, int> &char_count) {
    int score = 0;
    for (const auto &entry : char_count) {
        score += SCORES[entry.first - 'a'] * entry.second;
    }
    return score;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        cout << "Usage: ./hw2_large large.txt" << endl;
        return 1;
    }

    string input_file = argv[1];
    string dictionary_file = "words.txt";
    string output_file = "large_answer.txt";

    // 辞書を読み込む
    ifstream dict_fp(dictionary_file);
    if (!dict_fp) {
        cerr << "Failed to open words.txt" << endl;
        return 1;
    }

    vector<WordHash> word_hash_list;
    string line;
    while (getline(dict_fp, line)) {
        WordHash wh;
        wh.word = line;
        wh.char_count = count_characters(line);
        word_hash_list.push_back(wh);
    }
    dict_fp.close();

    // 入力ファイルを読み込む
    ifstream input_fp(input_file);
    if (!input_fp) {
        cerr << "Failed to open input file" << endl;
        return 1;
    }

    ofstream output_fp(output_file);
    if (!output_fp) {
        cerr << "Failed to open output file" << endl;
        input_fp.close();
        return 1;
    }

    while (getline(input_fp, line)) {
        unordered_map<char, int> input_char_count = count_characters(line);

        int max_score = 0;
        string best_word;

        for (const auto &wh : word_hash_list) {
            if (is_anagram(input_char_count, wh.char_count)) {
                int score = calculate_score(wh.char_count);
                if (score > max_score) {
                    max_score = score;
                    best_word = wh.word;
                }
            }
        }

        if (!best_word.empty()) {
            output_fp << best_word << endl;
        }
    }

    input_fp.close();
    output_fp.close();

    return 0;
}