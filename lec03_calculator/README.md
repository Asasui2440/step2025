# **第3回 Calculator (モジュール化)**

### 概要

標準入力から四則演算の文字列を受け取ったら、計算して結果を返すプログラム。

括弧を含む計算、abs,round,int関数に対応している。

**ファイル**  
`calculator.py` .. 計算機のプログラム  
`test_calculator.py`.. テストを実行するプログラム  



実行コマンド

```python
python calculator.py
```

入力例

```python
> 1+2*3
answer = 7.000000

> abs(-5) + round(2.7)
answer = 8.000000
```

不正な入力はエラーを返す

```python
> 2*
InvalidSyntaxError: Invalid syntax for the removal sign

> absc(2)
InvalidSyntaxError: Invalid character found: a

>(2+3))
InvalidSyntaxError: Mismatched parentheses
```


++2 - 3 など、先頭に+や-が続いてしまうものには対応できませんでした。

### テストの実行

```python
python -m unittest test_calculator.py
```

(++2 の時にうまくエラー処理ができていません)

```python
FAIL: test_invalid_syntax (test_calculator.TestCalculator.test_invalid_syntax) (case='++2-9*3')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/sui/2025/step/step2/anagram/lec03_calculator/test_calculator.py", line 46, in test_invalid_syntax
    with self.assertRaises(Exception):
AssertionError: Exception not raised

----------------------------------------------------------------------
Ran 5 tests in 0.001s

FAILED (failures=1)
```

## 実装詳細

文字列をToken化し、括弧、abs,round,int 、剰余*/ の順に計算していき、最後に残ったプラスマイナスの式を計算する。

括弧の関数で、括弧内の式を計算する時にevaluateを呼び出すことで、相互的な再帰処理を行なっている。

```python
def evaluate(tokens: list) -> float:
    tokens = evaluate_PAREN(tokens)
    tokens = evaluate_options(tokens)
    tokens = evaluate_times_divide(tokens)
		....
    return answer
```

### tokenクラスの定義

- 数字(Number)
- 演算子(Operand : Enum )
- absなど(MonoFunc : Enum)
