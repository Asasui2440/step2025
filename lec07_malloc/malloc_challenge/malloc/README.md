# 第7回  Malloc challenge 

**メモリ効率が良く、処理速度の速いmallocを実装する**    
- 詳細  https://github.com/hikalium/malloc_challenge/tree/main


## Files

- `simple_malloc.c`   
  デフォルトのプログラム。最初に見つけた空き領域にデータを格納する

- `malloc.c`  
  best fit + left/right merged  
  メモリを解放しようとする領域の両側が空き領域だった場合に結合する

- `list_bin_malloc.c`    
  best_fit + list bin  
  binを6つ作成し、データサイズによって使うbinを選択する。  
  データサイズ128byteがずば抜けて多かったので、128byteのみを格納するbinがある。

- `worst_fit_malloc.c`    
  メモリ効率を最も悪くする  
  格納したいデータのサイズ以上の空き領域の中で最も大きい空き領域を選ぶ


## 実行結果

**Time(ms) / Utilization(%)**   
| 実装ファイル        | Challenge 1      | Challenge 2      | Challenge 3      | Challenge 4       | Challenge 5       |
|------------------------|------------------|------------------|------------------|-------------------|-------------------|
| simple_malloc.c        | 8ms / 70%        | 4ms / 40%        | 74ms / 9%        | 10541ms / 15%     | 6197ms / 15%      |
| malloc.c               | 747ms / 70%      | 322ms / 40%      | 392ms / 51%      | 2659ms / **76%**      | 1410ms / **79%**      |
| best_fitのみ          | 1185ms / 70%     | 398ms / 40%     | 591ms / 50%     | 5493ms / 72%      | 3604ms / 75%      |
| list_bin_malloc.c           | 3261ms / 70%     | 3229ms / 40%     | 3307ms / 51%     | 3548ms / 72%      | 3619ms / 75%      |
| worst_fit_malloc.c     | 924ms / 70%      | 667ms / 40%      | 42131ms / 4%     | 671779ms / 7%     | 750911ms / 7%     |


## 考察
