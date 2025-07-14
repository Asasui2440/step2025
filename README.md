# STEP2025

This repository contains exercises for STEP2025.

### 📁 lec01: Anagram

1. `hw1.py`: Given a word, list all anagrams that can be formed from a dictionary.
2. `hw2.py`: Given a list of words (e.g., `small.txt`, `medium.txt`, `large.txt`), for each word, select the dictionary word that forms an anagram and yields the highest score, then output the result to a new file.

#### 📄 Files
- `words.txt`: Dictionary file
- `score_checker.py`: Script to verify the correctness of the results


### 📁 lec02: Hash Table
1. `hw1_hash_table.py`: Implements a hash table with the delete function, dynamic resizing of the table, and an improved hash calculation method.
2. `hw4_cache.py` : Implements a fixed-size cache that stores recently accessed web pages using a linked list.

### 📁 lec03: Calclator  
`calculator.py` : a simple calculator that evaluates mathematical expressions provided as strings.  
It supports:  
- Basic arithmetic operations: +, -, *, /  
- Parentheses for order of operations  
- Built-in functions: abs(), int(), round()  
- Invalid or unsafe expressions are rejected for security.

### 📁 lec04: Graph Algorithm
`wikipedia_graph.py`: 
- Find the shortest path with BFS
- Calculate the page ranks

### 📁 lec05: TSP challenge
Traveling Salesperson Problem    
`solver_opt.py` : Solving the problem using nearest neighbor methods and simulated Annealing  
<br>
In lec06, we tried 8192 cities.  

### 📁 lec07: Malloc Challenge
Create a my malloc
<br>
- `malloc.c`
   A merge algorithm is used to combine adjacent free memory blocks, aiming to optimize both memory utilization and throughput.

- `listbin.c` 
 Free memory blocks are managed in segregated free lists (bins) by size, enabling faster memory allocation and deallocation.

