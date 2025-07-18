## 宿題1

### ハッシュテーブルを実装する(hw1_hash_table.py)

### 追記内容

・putとgetは実装済みなので、deleteを書く<br>
・実行時間を早くするためにハッシュテーブルのサイズを変更する<br>
・hashを計算する方法を変更する<br>

### delete(self: HashTable, key: str, value: any) -> bool
**連結リスト**  
該当するitemが見つかったら削除してTrue、見つからなければFalseを返す

・消したいキーのハッシュ値を求める  
・該当するitemが先頭だったら、先頭をitem.nextにする  
・それ以外の時、前のitemのnextを、該当のitemのnextに変更する  

### change_hash_table_size(self : HashTable) -> None

・putとdeleteに書いてテーブルサイズを調整する  
・要素がテーブルサイズの70%を上回ったら、テーブルサイズを2倍にする。  
・要素がテーブルサイズの30%を下回ったら、テーブルサイズを1/2にする  

**注意点**
70%になって、テーブルサイズを2倍にすると、要素数はテーブルサイズの35%
→ここで、もしテーブルサイズの40%を下回ったらサイズを1/2にするという条件にすると、毎回リハッシュすることになる  
・その時、新たにテーブルに要素を入れ直す  
  
### ハッシュ関数の改良
  
```
calculate_hash(key : str) -> int
・hash += ord(key[i]) * i * (i + i % 2)
```
  
とにかく毎回違う数字が足されるように考えた。
実行時間はループ 80回くらいまでは 1秒未満だった  
途中、計算時間がかかっている時があり、その時はリハッシュが行われたのだと考えられる。今回はiが大きくても10程度なので、もっと大きい値になるように計算した方がいいかもしれない


## 宿題2

### ハッシュテーブルより木構造の方が多く使われる理由は何か？

・データの探索が容易

木構造はどこになんのデータがあるのか場所がある程度わかる。
ハッシュだと、ハッシュ値が完全にランダムになってしまうので保存の位置がバラバラ
(キーを指定すればアクセスできるので関係ない？)  
・ハッシュだと、ハッシュテーブルのサイズを変えるときに要素を全て入れ直さなくてはならない  

**オフィスアワー後追記：**

・木構造は範囲の特定に強い    
親ノードを削除すれば、ある範囲のデータを一気に削除することができる(?)   
logNでできる。要素の数もわかる   
親に対して、子供がたくさんある木だと、キャッシュすることによってアクセスが速くすることができる    
<br>
・ハッシュだと、ハッシュテーブルのサイズを変えるときに要素を全て入れ直さなくてはならない  
→その時に何秒以内に返すという要件があった場合、満たさなくなってしまう


## 宿題3

### キャッシュを実装するデータ構造を考える

### **オフィスアワー後追記：**

・連結リストで、ハッシュにポインタを持たせるとO(1)で行うことが可能  
・双方向リストにするやり方もある

どちらも未実装なので、これから時間作ってやりたいです  
以下で、自分で考えたものはO(N)でした。
  
**◯連結リストで更新していく**  
・キャッシュにない要素が来たらポインタを先頭につける    
・キャッシュにもうある場合は、一度その要素を削除してから先頭に付け直す  
・キャッシュよりサイズが大きくなってしまったら、末尾の要素を削除する  

**◯番号を持たせてリストで管理**  
・連結リストと同じ要領で番号を管理する  
・キャッシュにない要素がきたら1を持たせて、その後の要素の番号を1つさげていく。  
・キャッシュにある要素が来たら、それまでの要素の数字を下げて、該当の要素の数字を1にする  
・キャッシュサイズを超えたら、キャッシュサイズより大きな値を持った要素を削除する  
・番号順にソート  

どちらの二つもキャッシュのサイズだけループを回す必要がある


### 宿題4

**キャッシュ(hw4_chache.py)**   
最近アクセスされた順にページをキャッシュしていく  
双方向リストで実装

**クラス：Page**  
- `self.url` 　WebページのURL  
- `self.contents`  Webページの内容  
- `self.prev` 前のWebページ  
- `self.next`  次のWebページ  

**クラス：Cache**   
- `self.cache`　キャッシュの先頭のWebページ  
- `self.cache_size` キャッシュの最大サイズ  
- `self.size` キャッシュの現在の要素の数  
- `self.head` キャッシュの先頭のWebページ(ポインタ)  
- `self.tail` キャッシュの末尾のWebページ(ポインタ)  
- `self.hash_table` 辞書型。urlとcontentsの組みをkeyとして、Pageを返す  

**関数：access_page(self : Cache, url : str, contents : str) -> None**  
・キャッシュの更新を行う  
・該当のURLがキャッシュにあった場合、それを先頭に持ってくる  
・cache_sizeよりもself.sizeが大きくなってしまった場合、連結リストの最後の要素を削除する  

**関数：get_pages(self : Cache)**  
・access_pageで更新されたキャッシュについて、pageを先頭から順に辿っていってリストに追加していく
