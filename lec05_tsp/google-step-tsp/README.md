# 第5回  TSP challenge  

N個の点を全て辿るように始点へ戻るルートの中で、最小のものを探す  
詳細：  
https://github.com/hayatoito/google-step-tsp

**実行方法(例)**
```
python solver_opt.py input_0.csv > output_0.csv
```

### 実行ファイル solver_opt.py

- **greedy_multi_start**   
  貪欲法。min(100,N)回ランダムに開始点を選んで、最も良かったルートを採用
  
- **solve_opt2**     
2つの辺を組み替える(交差がなくなるまで行う)

- **solve_annealing**   
  焼きなまし法。初期温度= 初期の合計距離*0.3,alpha = 0.9995, 最終温度=1e-7  
  iterationごとにある確率で、2opt,3opt,or_optを行う  
  参考: https://qiita.com/take314/items/69b93481403feb857d6e

  - **or_opt**  
     ランダムに、長さ1~3の辺を取ってきて、どこかに挿入する
    
- **opt3_random**   
ランダムに3つ辺を取ってスコアが良くなったら採用。これをiteration回試す
  

**その他** 
- `lin_kernighan.py`
  k本の辺を組み替えて、一番よかったものを採用。まだ修正していないので動かない

<br>

### チャレンジ2
- `solve_greedy_multi_start`: 貪欲法を、10個の開始点から試して一番いいものを採用した。  
- opt3_randomは、5万回、3辺の繋ぎ直しを試みた。10万回にしたら若干悪くなったので5万回にしておいた。
- annealingは見たところ機能していなかったので、annealing + opt3_randomと、opt3_randomの違いは、greedyやopt3_randomのランダム性によるものだと考えられる。  
- 焼きなまし(annealing)のどこがおかしくて動いていないのかをおいおい考えていきたいです

<br>


| 手法                                             | N = 5 | N = 8 | N = 16 | N = 64 | N = 128 | N = 512 | N = 2048 |
|--------------------------------------------------|--------|--------|---------|---------|----------|-----------|------------|
| greedy_multi_start + opt2                        | 3418   | 3832   | 4821    | 8773    | 11272    | 21911     | 42465      |
| greedy_multi_start + opt2 + opt3_limited         | 3418   | 3832   | 5065    | 8657    | 11445    | 21975     | 42579      |
| greedy_multi_start + opt2 + opt3_random          | 3418   | 3832   | 4750    | 8612    | **11214**    | 22124     | 42747      |
| greedy_multi_start + opt2 + annealing            | 3418   | 3778   | 4494    | 8845    | 11460    | 22057     | 42605      |
| greedy_multi_start + opt2 + annealing + opt3_random | 3418 | 3778   | 4494    | **8520**    | 11262    | **22052**     | **42348**      |

<br>

### チャレンジ3

- annealingが成功。一番良い結果になった。
- annealingが機能していなかった理由は、opt2の関数内でtour= tour[:]　のようにtourを一回コピーする必要があったらしいですが  
なぜなのかあまり理解できていません。tourを上書きしていくので元のtourが変わっても平気な気がしてしまいます。
- or_opt, 2optで10回ループを回していたが、そうではなくてannealing自体を10^8回くらい回した方が良い気がしてきた。 

### 追記
- Githubに上げてるsolver_opt.pyをもう一回実行してみたらやっぱりannealingがうまくいっていませんでした。  
- なぜうまくいった時があったのかがわかりません  




| 手法                                             | N = 5 | N = 8 | N = 16 | N = 64 | N = 128 | N = 512 | N = 2048 |
|--------------------------------------------------|--------|--------|---------|---------|----------|-----------|------------|
| greedy_multi_start + opt2 + annealing + opt3_random | 3418 | 3778   | 4494    | **8172**    | **10712**    | **21554**     | **42553**      |



### これからやりたいアルゴリズム
- 蟻コロニー
- 遺伝的アルゴリズム
  
