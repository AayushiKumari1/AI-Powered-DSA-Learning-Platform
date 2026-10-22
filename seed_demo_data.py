"""
Reset EduMentor's database and load clean demo data.

    python seed_demo_data.py            # backs up instance/site.db, then reseeds

What it creates
  * 16 topics with full lessons (intro, worked example, code, complexity notes)
  * 24 coding problems; every hidden test-case output is produced by running the
    reference solution below, so expected answers are always correct
  * 3 coding tests, 9 badges, 3 announcements
  * 8 learner accounts with realistic progress over the last 30 days
      demo login:  demo@edumentor.dev / demo1234
  * Admin console login is unchanged (admin / admin123, see routes/admin.py)

The previous database is copied to instance/site_backup_<timestamp>.db first.
"""
import io
import json
import os
import random
import shutil
import sys
from contextlib import redirect_stdout
from datetime import datetime, timedelta

os.environ.setdefault("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", "seed"))
os.environ.setdefault("YOUTUBE_API_KEY", os.environ.get("YOUTUBE_API_KEY", "seed"))

from werkzeug.security import generate_password_hash  # noqa: E402

# ---------------------------------------------------------------- lessons
def lesson(intro, example, code, details):
    return f"""
<section><h4>Introduction</h4><p>{intro}</p></section>
<section><h4>Example / Explanation</h4><p>{example}</p></section>
<section><h4>Code Example</h4><pre><code>{code}</code></pre></section>
<section><h4>Additional Details</h4><p>{details}</p></section>
""".strip()


TOPICS = [
    ("Arrays", "arrays, traversal, prefix-sum", lesson(
        "An array stores elements in contiguous memory, so any index can be read in O(1). Most DSA patterns start here: traversal, prefix sums and in-place updates.",
        "To answer many range-sum queries on <code>[2, 4, 1, 7]</code>, build a prefix array <code>[0, 2, 6, 7, 14]</code>. The sum of indices 1..3 is <code>prefix[4] - prefix[1] = 12</code>.",
        "def prefix_sums(nums):\n    prefix = [0]\n    for x in nums:\n        prefix.append(prefix[-1] + x)\n    return prefix\n\ndef range_sum(prefix, l, r):\n    return prefix[r + 1] - prefix[l]",
        "Access O(1), search O(n), insert/delete in the middle O(n). Prefix sums trade O(n) extra space for O(1) range queries. Watch for off-by-one errors at the boundaries.")),
    ("Strings", "strings, palindrome, frequency", lesson(
        "A string is a sequence of characters. Interview problems usually combine traversal with a frequency count or a two-pointer check.",
        "<code>\"racecar\"</code> is a palindrome: compare characters from both ends moving inwards. An anagram check compares character counts of two strings.",
        "from collections import Counter\n\ndef is_anagram(a, b):\n    return Counter(a) == Counter(b)\n\ndef is_palindrome(s):\n    return s == s[::-1]",
        "Strings are immutable in Python and Java, so repeated concatenation in a loop is O(n²). Build a list and join it instead. Counting with a fixed 26-slot array is O(1) space for lowercase letters.")),
    ("Hashing", "hash map, hash set, counting", lesson(
        "Hash maps store key → value pairs with average O(1) lookup. They turn many O(n²) “search for a partner” problems into a single O(n) pass.",
        "Two Sum: while scanning <code>[2, 7, 11, 15]</code> for target 9, store each value's index. At 7 we look up <code>9 - 7 = 2</code>, which is already in the map.",
        "def two_sum(nums, target):\n    seen = {}\n    for i, x in enumerate(nums):\n        if target - x in seen:\n            return [seen[target - x], i]\n        seen[x] = i",
        "Average O(1) insert and lookup, O(n) worst case on heavy collisions. Use a set when you only need membership. Keys must be immutable (tuples, not lists).")),
    ("Two Pointers", "two pointers, sorted array, in-place", lesson(
        "Two indices move through the data, often from both ends or at different speeds, to avoid nested loops.",
        "To check whether a sorted array has a pair summing to 10, start <code>l</code> at the left and <code>r</code> at the right. If the sum is too small move <code>l</code> right; if too large move <code>r</code> left.",
        "def pair_with_sum(nums, target):\n    l, r = 0, len(nums) - 1\n    while l < r:\n        s = nums[l] + nums[r]\n        if s == target:\n            return l, r\n        if s < target:\n            l += 1\n        else:\n            r -= 1\n    return None",
        "Usually O(n) time and O(1) space. Requires sorted input or a monotonic property. Fast/slow pointers detect cycles in linked lists.")),
    ("Sliding Window", "sliding window, substring, subarray", lesson(
        "A window [left, right] slides over the array; expand right to include elements and shrink left when a condition breaks.",
        "Longest substring without repeats in <code>\"abcabcbb\"</code>: expand while characters are unique; when a repeat appears, move left past its previous position. Best length is 3.",
        "def longest_unique(s):\n    last, left, best = {}, 0, 0\n    for right, ch in enumerate(s):\n        if ch in last and last[ch] >= left:\n            left = last[ch] + 1\n        last[ch] = right\n        best = max(best, right - left + 1)\n    return best",
        "Each element enters and leaves the window once, so O(n). Fixed-size windows are simpler: add the new element, remove the outgoing one.")),
    ("Stack", "stack, LIFO, monotonic stack", lesson(
        "A stack is last-in, first-out. It is ideal for matching brackets, undo operations and “next greater element” style problems.",
        "For <code>\"([]{})\"</code>, push every opener and pop when a closer arrives; each pop must match. The string is valid if the stack ends empty.",
        "def is_valid(s):\n    pairs = {')': '(', ']': '[', '}': '{'}\n    stack = []\n    for ch in s:\n        if ch in pairs:\n            if not stack or stack.pop() != pairs[ch]:\n                return False\n        else:\n            stack.append(ch)\n    return not stack",
        "Push and pop are O(1). A monotonic stack keeps elements in sorted order and solves next-greater/smaller problems in O(n).")),
    ("Queue", "queue, FIFO, BFS", lesson(
        "A queue is first-in, first-out. It powers breadth-first search, scheduling and stream processing.",
        "Level-order traversal of a tree enqueues the root, then repeatedly dequeues a node and enqueues its children, visiting nodes level by level.",
        "from collections import deque\n\ndef bfs(start, graph):\n    seen, q, order = {start}, deque([start]), []\n    while q:\n        node = q.popleft()\n        order.append(node)\n        for nxt in graph[node]:\n            if nxt not in seen:\n                seen.add(nxt)\n                q.append(nxt)\n    return order",
        "Use <code>collections.deque</code> in Python: <code>list.pop(0)</code> is O(n). Enqueue/dequeue are O(1).")),
    ("Linked List", "linked list, pointers, reversal", lesson(
        "Each node stores a value and a pointer to the next node. Insertions are O(1) once you hold the node, but access by index is O(n).",
        "Reversing <code>1 → 2 → 3</code>: walk the list keeping <code>prev</code>, and point each node back to <code>prev</code>. The result is <code>3 → 2 → 1</code>.",
        "def reverse(head):\n    prev = None\n    while head:\n        head.next, prev, head = prev, head, head.next\n    return prev",
        "Draw the pointers before coding. A dummy head node removes edge cases when the head itself may change. Fast/slow pointers find the middle or detect a cycle.")),
    ("Binary Search", "binary search, sorted, log n", lesson(
        "Binary search halves the search space each step, finding a target in a sorted array in O(log n).",
        "Searching 7 in <code>[1, 3, 5, 7, 9]</code>: middle is 5, so search the right half; the next middle is 7. Found in two steps.",
        "def binary_search(nums, target):\n    lo, hi = 0, len(nums) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if nums[mid] == target:\n            return mid\n        if nums[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1",
        "The pattern also works on answers: “find the smallest x for which condition(x) is true” when the condition is monotonic. Be precise about <code>lo <= hi</code> vs <code>lo < hi</code>.")),
    ("Recursion", "recursion, base case, backtracking", lesson(
        "A recursive function solves a problem by calling itself on smaller inputs until it reaches a base case.",
        "<code>fib(5) = fib(4) + fib(3)</code>, down to <code>fib(1) = 1</code> and <code>fib(0) = 0</code>. Without caching this repeats work exponentially.",
        "from functools import lru_cache\n\n@lru_cache(maxsize=None)\ndef fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)",
        "Always define the base case first. Each call uses stack space, so depth n costs O(n) memory; Python's default limit is about 1000 frames.")),
    ("Sorting", "sorting, merge sort, quick sort", lesson(
        "Sorting arranges data in order and often unlocks simpler solutions such as two pointers or greedy choices.",
        "Merge sort splits <code>[5, 2, 4, 1]</code> into halves, sorts each, then merges <code>[2, 5]</code> and <code>[1, 4]</code> into <code>[1, 2, 4, 5]</code>.",
        "def merge_sort(a):\n    if len(a) <= 1:\n        return a\n    mid = len(a) // 2\n    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])\n    out, i, j = [], 0, 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            out.append(left[i]); i += 1\n        else:\n            out.append(right[j]); j += 1\n    return out + left[i:] + right[j:]",
        "Merge sort is O(n log n) and stable; quick sort is O(n log n) on average but O(n²) worst case. Built-in sorts (Timsort) are usually the right choice.")),
    ("Trees", "binary tree, DFS, traversal", lesson(
        "A binary tree node has up to two children. Most tree problems are solved with recursion: solve for the children, then combine.",
        "Maximum depth = 1 + max(depth(left), depth(right)). For a tree with root 3, children 9 and 20, and 20 having children 15 and 7, the depth is 3.",
        "def max_depth(node):\n    if node is None:\n        return 0\n    return 1 + max(max_depth(node.left), max_depth(node.right))",
        "Traversals: preorder (node, left, right), inorder (left, node, right — sorted for a BST), postorder, and level-order with a queue.")),
    ("Heap", "heap, priority queue, top-k", lesson(
        "A heap keeps the smallest (or largest) element at the top, with O(log n) insert and remove.",
        "To find the 2nd largest in <code>[3, 2, 1, 5, 6, 4]</code>, keep a min-heap of size 2. After scanning, the heap holds <code>[5, 6]</code> and its top, 5, is the answer.",
        "import heapq\n\ndef kth_largest(nums, k):\n    heap = []\n    for x in nums:\n        heapq.heappush(heap, x)\n        if len(heap) > k:\n            heapq.heappop(heap)\n    return heap[0]",
        "Top-k problems run in O(n log k). Python's heapq is a min-heap; push negatives for a max-heap.")),
    ("Graphs", "graph, BFS, DFS, connected components", lesson(
        "A graph is a set of nodes connected by edges. Represent it as an adjacency list and explore it with BFS or DFS.",
        "Counting islands in a grid: every unvisited land cell starts a DFS that marks its whole island, and each start increments the count.",
        "def count_islands(grid):\n    rows, cols = len(grid), len(grid[0])\n    def sink(r, c):\n        if 0 <= r < rows and 0 <= c < cols and grid[r][c] == '1':\n            grid[r][c] = '0'\n            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):\n                sink(r + dr, c + dc)\n    count = 0\n    for r in range(rows):\n        for c in range(cols):\n            if grid[r][c] == '1':\n                count += 1\n                sink(r, c)\n    return count",
        "BFS finds shortest paths in unweighted graphs; Dijkstra handles weights. Topological sort orders tasks with dependencies and detects cycles.")),
    ("Dynamic Programming", "dynamic programming, memoization, tabulation", lesson(
        "DP solves problems with overlapping subproblems by storing answers to smaller cases instead of recomputing them.",
        "Climbing stairs with steps of 1 or 2: <code>ways(n) = ways(n-1) + ways(n-2)</code>. For n = 4 the table is 1, 1, 2, 3, 5.",
        "def climb_stairs(n):\n    a, b = 1, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a",
        "Define the state, the transition and the base cases. Start top-down with memoization, then convert to a bottom-up table to save stack space.")),
    ("Greedy", "greedy, intervals, scheduling", lesson(
        "A greedy algorithm makes the locally best choice at each step. It works when local choices provably lead to a global optimum.",
        "To attend the most meetings, sort them by end time and always pick the next meeting that starts after the last chosen one ends.",
        "def max_meetings(intervals):\n    intervals.sort(key=lambda m: m[1])\n    count, end = 0, float('-inf')\n    for s, e in intervals:\n        if s >= end:\n            count, end = count + 1, e\n    return count",
        "Greedy is usually O(n log n) because of sorting. If you can't argue why the greedy choice is safe, try DP instead (coin change with odd coins breaks greedy).")),
]

# ---------------------------------------------------------------- problems
# Each problem: title (contains its ML topic name), difficulty, description, solution(stdin)->stdout, inputs
def ints(line):
    return list(map(int, line.split())) if line.strip() else []


def sol_sum(s):
    l = s.split("\n"); return str(sum(ints(l[1]) if len(l) > 1 else []))
def sol_max(s):
    l = s.split("\n"); return str(max(ints(l[1])))
def sol_two_sum(s):
    l = s.split("\n"); a = ints(l[1]); t = int(l[2]); seen = {}
    for i, x in enumerate(a):
        if t - x in seen: return f"{seen[t - x]} {i}"
        seen[x] = i
def sol_kadane(s):
    a = ints(s.split("\n")[1]); best = cur = a[0]
    for x in a[1:]: cur = max(x, cur + x); best = max(best, cur)
    return str(best)
def sol_merge(s):
    l = s.split("\n"); return " ".join(map(str, sorted(ints(l[1]) + ints(l[3]))))
def sol_pal(s):
    t = [c.lower() for c in s.split("\n")[0] if c.isalnum()]; return "true" if t == t[::-1] else "false"
def sol_vowels(s):
    return str(sum(c in "aeiouAEIOU" for c in s.split("\n")[0]))
def sol_anagram(s):
    l = s.split("\n"); return "true" if sorted(l[0]) == sorted(l[1]) else "false"
def sol_longest(s):
    t = s.split("\n")[0]; last, left, best = {}, 0, 0
    for r, c in enumerate(t):
        if c in last and last[c] >= left: left = last[c] + 1
        last[c] = r; best = max(best, r - left + 1)
    return str(best)
def sol_dedup(s):
    a = ints(s.split("\n")[1]); u = sorted(set(a)); return f"{len(u)}\n{' '.join(map(str, u))}"
def sol_reverse(s):
    return " ".join(map(str, ints(s.split("\n")[1])[::-1]))
def sol_parens(s):
    pairs = {")": "(", "]": "[", "}": "{"}; st = []
    for c in s.split("\n")[0]:
        if c in pairs:
            if not st or st.pop() != pairs[c]: return "false"
        else: st.append(c)
    return "true" if not st else "false"
def sol_nge(s):
    a = ints(s.split("\n")[1]); res = [-1] * len(a); st = []
    for i, x in enumerate(a):
        while st and a[st[-1]] < x: res[st.pop()] = x
        st.append(i)
    return " ".join(map(str, res))
def sol_first_unique(s):
    from collections import Counter, deque
    cnt, q, out = Counter(), deque(), []
    for c in s.split("\n")[0]:
        cnt[c] += 1; q.append(c)
        while q and cnt[q[0]] > 1: q.popleft()
        out.append(q[0] if q else "#")
    return "".join(out)
def sol_middle(s):
    a = ints(s.split("\n")[1]); return str(a[len(a) // 2])
def sol_rev_list(s):
    return " ".join(map(str, ints(s.split("\n")[1])[::-1]))
def sol_bsearch(s):
    l = s.split("\n"); a = ints(l[1]); t = int(l[2]); lo, hi = 0, len(a) - 1
    while lo <= hi:
        m = (lo + hi) // 2
        if a[m] == t: return str(m)
        lo, hi = (m + 1, hi) if a[m] < t else (lo, m - 1)
    return "-1"
def sol_insert(s):
    import bisect; l = s.split("\n"); return str(bisect.bisect_left(ints(l[1]), int(l[2])))
def sol_fib(s):
    n = int(s.strip()); a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return str(a)
def sol_depth(s):
    vals = s.split("\n")[0].split()
    if not vals or vals[0] == "null": return "0"
    # level-order array; depth = number of levels containing a real node
    nodes, depth, i, level = [vals[0]], 1, 1, [0]
    from collections import deque
    q = deque([(vals[0], 1)]); best = 1
    while q and i < len(vals):
        _, d = q.popleft()
        for _ in range(2):
            if i < len(vals):
                if vals[i] != "null": q.append((vals[i], d + 1)); best = max(best, d + 1)
                i += 1
    return str(best)
def sol_kth(s):
    import heapq; l = s.split("\n"); n, k = ints(l[0]); return str(heapq.nlargest(k, ints(l[1]))[-1])
def sol_islands(s):
    l = s.split("\n"); r, c = ints(l[0]); g = [list(row) for row in l[1:1 + r]]; cnt = 0
    def sink(i, j):
        st = [(i, j)]
        while st:
            a, b = st.pop()
            if 0 <= a < r and 0 <= b < c and g[a][b] == "1":
                g[a][b] = "0"; st += [(a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)]
    for i in range(r):
        for j in range(c):
            if g[i][j] == "1": cnt += 1; sink(i, j)
    return str(cnt)
def sol_course(s):
    from collections import deque
    l = s.split("\n"); n, m = ints(l[0]); adj = [[] for _ in range(n)]; indeg = [0] * n
    for k in range(m):
        a, b = ints(l[1 + k]); adj[b].append(a); indeg[a] += 1
    q = deque(i for i in range(n) if indeg[i] == 0); seen = 0
    while q:
        x = q.popleft(); seen += 1
        for y in adj[x]:
            indeg[y] -= 1
            if indeg[y] == 0: q.append(y)
    return "true" if seen == n else "false"
def sol_climb(s):
    n = int(s.strip()); a, b = 1, 1
    for _ in range(n): a, b = b, a + b
    return str(a)
def sol_coins(s):
    l = s.split("\n"); coins = ints(l[1]); amt = int(l[2]); INF = 10 ** 9; dp = [0] + [INF] * amt
    for x in range(1, amt + 1):
        for c in coins:
            if c <= x and dp[x - c] + 1 < dp[x]: dp[x] = dp[x - c] + 1
    return str(dp[amt] if dp[amt] < INF else -1)
def sol_lcs(s):
    l = s.split("\n"); a, b = l[0], l[1]; dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
    return str(dp[-1][-1])


def fmt(intro, inp, out, constraints):
    return (f"<p>{intro}</p><h4>Input</h4><p>{inp}</p><h4>Output</h4><p>{out}</p>"
            f"<h4>Constraints</h4><ul>{''.join(f'<li>{c}</li>' for c in constraints)}</ul>")


PROBLEMS = [
    ("Arrays: Sum of Elements", "easy", fmt("Given an array of integers, print the sum of all its elements.", "First line: <code>n</code>. Second line: <code>n</code> space-separated integers.", "A single integer, the sum.", ["1 ≤ n ≤ 10⁵", "-10⁴ ≤ a[i] ≤ 10⁴"]),
     sol_sum, ["5\n1 2 3 4 5", "1\n-7", "4\n-1 -2 3 10", "6\n10000 10000 10000 -5 0 5"]),
    ("Arrays: Maximum Element", "easy", fmt("Print the largest element of the array.", "First line: <code>n</code>. Second line: <code>n</code> integers.", "The maximum value.", ["1 ≤ n ≤ 10⁵"]),
     sol_max, ["5\n3 9 2 7 1", "1\n42", "4\n-5 -2 -9 -3", "6\n4 4 4 4 4 4"]),
    ("Arrays: Two Sum", "easy", fmt("Find the indices of the two numbers that add up to <code>target</code>. Exactly one solution exists; print the smaller index first.", "Line 1: <code>n</code>. Line 2: <code>n</code> integers. Line 3: <code>target</code>.", "Two 0-based indices separated by a space.", ["2 ≤ n ≤ 10⁴", "Exactly one valid pair"]),
     sol_two_sum, ["4\n2 7 11 15\n9", "3\n3 2 4\n6", "2\n3 3\n6", "6\n-3 4 3 90 1 8\n0"]),
    ("Arrays: Maximum Subarray Sum", "medium", fmt("Find the contiguous subarray with the largest sum and print that sum (Kadane's algorithm).", "Line 1: <code>n</code>. Line 2: <code>n</code> integers.", "The maximum subarray sum.", ["1 ≤ n ≤ 10⁵", "-10⁴ ≤ a[i] ≤ 10⁴"]),
     sol_kadane, ["9\n-2 1 -3 4 -1 2 1 -5 4", "1\n1", "5\n5 4 -1 7 8", "4\n-3 -1 -4 -2"]),
    ("Arrays: Merge Two Sorted Arrays", "easy", fmt("Merge two sorted arrays into one sorted array.", "Line 1: <code>n</code>, line 2: first array. Line 3: <code>m</code>, line 4: second array.", "The merged array, space-separated.", ["1 ≤ n, m ≤ 10⁴"]),
     sol_merge, ["3\n1 3 5\n3\n2 4 6", "1\n1\n4\n2 3 4 5", "4\n-2 0 0 9\n2\n-5 10", "2\n1 1\n2\n1 1"]),
    ("Strings: Valid Palindrome", "easy", fmt("Ignoring case and non-alphanumeric characters, decide whether the string reads the same backwards.", "A single line containing the string.", "<code>true</code> or <code>false</code>.", ["1 ≤ length ≤ 2·10⁵"]),
     sol_pal, ["A man, a plan, a canal: Panama", "race a car", "x", "No lemon, no melon"]),
    ("Strings: Count Vowels", "easy", fmt("Count the vowels (a, e, i, o, u in either case) in the string.", "A single line.", "The number of vowels.", ["1 ≤ length ≤ 10⁵"]),
     sol_vowels, ["hello world", "EduMentor", "rhythm", "AEIOUaeiou"]),
    ("Strings: Valid Anagram", "easy", fmt("Two lowercase strings are given. Print whether the second is an anagram of the first.", "Two lines, one string each.", "<code>true</code> or <code>false</code>.", ["1 ≤ length ≤ 5·10⁴"]),
     sol_anagram, ["anagram\nnagaram", "rat\ncar", "a\na", "listen\nsilentt"]),
    ("Strings: Longest Substring Without Repeating Characters", "medium", fmt("Print the length of the longest substring that contains no repeated characters.", "A single line.", "The length.", ["1 ≤ length ≤ 5·10⁴", "Hint: sliding window"]),
     sol_longest, ["abcabcbb", "bbbbb", "pwwkew", "dvdf"]),
    ("Two Pointers: Remove Duplicates from Sorted Array", "easy", fmt("Given a sorted array, print how many unique values it has, then the unique values in order.", "Line 1: <code>n</code>. Line 2: <code>n</code> sorted integers.", "Line 1: <code>k</code>. Line 2: the <code>k</code> unique values.", ["1 ≤ n ≤ 3·10⁴", "Solve it in O(1) extra space"]),
     sol_dedup, ["3\n1 1 2", "10\n0 0 1 1 1 2 2 3 3 4", "1\n5", "4\n-1 -1 -1 -1"]),
    ("Two Pointers: Reverse an Array", "easy", fmt("Reverse the array in place by swapping from both ends.", "Line 1: <code>n</code>. Line 2: <code>n</code> integers.", "The reversed array.", ["1 ≤ n ≤ 10⁵"]),
     sol_reverse, ["5\n1 2 3 4 5", "1\n9", "4\n-1 0 1 2", "6\n6 5 4 3 2 1"]),
    ("Stack: Valid Parentheses", "easy", fmt("Given a string of brackets <code>()[]{}</code>, decide whether every bracket is closed in the correct order.", "A single line.", "<code>true</code> or <code>false</code>.", ["1 ≤ length ≤ 10⁴"]),
     sol_parens, ["()[]{}", "(]", "([{}])", "(((", "]"]),
    ("Stack: Next Greater Element", "medium", fmt("For each element print the first larger element to its right, or -1 if none exists.", "Line 1: <code>n</code>. Line 2: <code>n</code> integers.", "<code>n</code> values separated by spaces.", ["1 ≤ n ≤ 10⁵", "Hint: monotonic stack"]),
     sol_nge, ["4\n4 5 2 25", "4\n13 7 6 12", "1\n5", "5\n1 2 3 4 5"]),
    ("Queue: First Non-Repeating Character in a Stream", "medium", fmt("Characters arrive one by one. After each character, print the first character so far that has appeared exactly once, or <code>#</code> if none.", "A single lowercase string.", "A string of the same length.", ["1 ≤ length ≤ 10⁵"]),
     sol_first_unique, ["aabc", "zz", "abcabc", "leetcode"]),
    ("Linked List: Middle of the List", "easy", fmt("The values of a singly linked list are given in order. Print the middle node's value; for an even length, print the second middle.", "Line 1: <code>n</code>. Line 2: <code>n</code> values.", "The middle value.", ["1 ≤ n ≤ 100", "Hint: fast and slow pointers"]),
     sol_middle, ["5\n1 2 3 4 5", "6\n1 2 3 4 5 6", "1\n7", "2\n10 20"]),
    ("Linked List: Reverse a Linked List", "easy", fmt("Reverse the linked list and print its values from head to tail.", "Line 1: <code>n</code>. Line 2: <code>n</code> values.", "The reversed values.", ["1 ≤ n ≤ 5000"]),
     sol_rev_list, ["5\n1 2 3 4 5", "2\n1 2", "1\n0", "4\n9 8 8 9"]),
    ("Binary Search: Find Target Index", "easy", fmt("Search a sorted array of distinct integers for <code>target</code>. Print its index, or -1.", "Line 1: <code>n</code>. Line 2: sorted integers. Line 3: <code>target</code>.", "The index or -1.", ["1 ≤ n ≤ 10⁴", "Expected O(log n)"]),
     sol_bsearch, ["6\n-1 0 3 5 9 12\n9", "6\n-1 0 3 5 9 12\n2", "1\n5\n5", "5\n1 3 5 7 9\n1"]),
    ("Binary Search: Search Insert Position", "medium", fmt("Print the index where <code>target</code> is, or where it would be inserted to keep the array sorted.", "Line 1: <code>n</code>. Line 2: sorted distinct integers. Line 3: <code>target</code>.", "An index.", ["1 ≤ n ≤ 10⁴"]),
     sol_insert, ["4\n1 3 5 6\n5", "4\n1 3 5 6\n2", "4\n1 3 5 6\n7", "4\n1 3 5 6\n0"]),
    ("Recursion: Fibonacci Number", "easy", fmt("Print F(n) where F(0) = 0, F(1) = 1 and F(n) = F(n-1) + F(n-2).", "A single integer <code>n</code>.", "F(n).", ["0 ≤ n ≤ 50"]),
     sol_fib, ["2", "10", "0", "30"]),
    ("Trees: Maximum Depth of Binary Tree", "medium", fmt("A binary tree is given in level order, with <code>null</code> for missing children. Print its maximum depth.", "A single line of space-separated values.", "The depth (0 for an empty tree).", ["0 ≤ nodes ≤ 10⁴"]),
     sol_depth, ["3 9 20 null null 15 7", "1 null 2", "null", "1 2 3 4 null null null 5"]),
    ("Heap: Kth Largest Element", "medium", fmt("Print the k-th largest element of the array (in sorted order, not the k-th distinct).", "Line 1: <code>n k</code>. Line 2: <code>n</code> integers.", "The k-th largest value.", ["1 ≤ k ≤ n ≤ 10⁵", "Hint: min-heap of size k"]),
     sol_kth, ["6 2\n3 2 1 5 6 4", "9 4\n3 2 3 1 2 4 5 5 6", "1 1\n7", "5 5\n-1 -2 -3 -4 -5"]),
    ("Graphs: Number of Islands", "medium", fmt("A grid of <code>1</code> (land) and <code>0</code> (water) is given. Count the islands; land connects horizontally and vertically.", "Line 1: <code>rows cols</code>. Then <code>rows</code> lines of digits without spaces.", "The number of islands.", ["1 ≤ rows, cols ≤ 300"]),
     sol_islands, ["4 5\n11110\n11010\n11000\n00000", "4 5\n11000\n11000\n00100\n00011", "1 1\n0", "3 3\n101\n010\n101"]),
    ("Graphs: Course Schedule", "hard", fmt("There are <code>n</code> courses and <code>m</code> prerequisite pairs <code>a b</code> meaning “take b before a”. Print whether all courses can be finished.", "Line 1: <code>n m</code>. Next <code>m</code> lines: <code>a b</code>.", "<code>true</code> or <code>false</code>.", ["1 ≤ n ≤ 2000", "Hint: topological sort / cycle detection"]),
     sol_course, ["2 1\n1 0", "2 2\n1 0\n0 1", "4 3\n1 0\n2 1\n3 2", "3 3\n0 1\n1 2\n2 0"]),
    ("Dynamic Programming: Climbing Stairs", "easy", fmt("You can climb 1 or 2 steps at a time. In how many distinct ways can you reach step <code>n</code>?", "A single integer <code>n</code>.", "The number of ways.", ["1 ≤ n ≤ 45"]),
     sol_climb, ["2", "3", "5", "45"]),
    ("Dynamic Programming: Coin Change", "medium", fmt("Print the fewest coins needed to make <code>amount</code>, or -1 if it can't be made. Coins can be reused.", "Line 1: number of coin types. Line 2: coin values. Line 3: <code>amount</code>.", "The minimum number of coins, or -1.", ["1 ≤ coins ≤ 12", "0 ≤ amount ≤ 10⁴"]),
     sol_coins, ["3\n1 2 5\n11", "1\n2\n3", "1\n1\n0", "3\n1 3 4\n6"]),
    ("Dynamic Programming: Longest Common Subsequence", "hard", fmt("Print the length of the longest subsequence common to both strings.", "Two lines, one string each.", "The LCS length.", ["1 ≤ length ≤ 1000"]),
     sol_lcs, ["abcde\nace", "abc\nabc", "abc\ndef", "AGGTAB\nGXTXAYB"]),
]

TESTS = [
    ("Arrays & Strings Fundamentals", "A warm-up assessment on traversal, hashing and string basics.",
     ["Arrays: Sum of Elements", "Arrays: Two Sum", "Strings: Valid Palindrome", "Strings: Valid Anagram", "Two Pointers: Remove Duplicates from Sorted Array"],
     ["Arrays", "Strings", "Hashing", "Two Pointers"]),
    ("Stacks, Queues & Searching", "Monotonic stacks, streams and binary search under time pressure.",
     ["Stack: Valid Parentheses", "Stack: Next Greater Element", "Queue: First Non-Repeating Character in a Stream", "Binary Search: Search Insert Position"],
     ["Stack", "Queue", "Binary Search"]),
    ("Interview Ready: Mixed Problems", "A realistic mix across heaps, graphs and dynamic programming.",
     ["Arrays: Maximum Subarray Sum", "Heap: Kth Largest Element", "Graphs: Number of Islands", "Dynamic Programming: Coin Change", "Dynamic Programming: Longest Common Subsequence"],
     ["Arrays", "Heap", "Graphs", "Dynamic Programming"]),
]

ANNOUNCEMENTS = [
    ("Welcome to the new EduMentor", "We've redesigned the whole platform. Try the AI mentor on any page — it gives hints first, and full solutions only when you ask.", 12),
    ("New test: Interview Ready", "A mixed assessment covering heaps, graphs and dynamic programming is now live under Tests. It's proctored, so keep your camera on.", 4),
    ("Weekend practice challenge", "Solve any three medium problems before Sunday night and post your approach in #dynamic-programming.", 1),
]

LEARNERS = [  # username, email, skill 0..1
    ("demo", "demo@edumentor.dev", 0.6),
    ("priya_sharma", "priya@example.com", 0.85),
    ("rahul_verma", "rahul@example.com", 0.7),
    ("ananya_iyer", "ananya@example.com", 0.55),
    ("arjun_mehta", "arjun@example.com", 0.45),
    ("sneha_patil", "sneha@example.com", 0.35),
    ("kabir_singh", "kabir@example.com", 0.25),
    ("meera_nair", "meera@example.com", 0.15),
]

CODE_OK = {
    "python": "import sys\n\ndef solve():\n    data = sys.stdin.read().split()\n    # accepted solution\n    print(data[0])\n\nsolve()\n",
    "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main(){\n    // accepted solution\n    return 0;\n}\n",
    "java": "import java.util.*;\npublic class Main {\n    public static void main(String[] a) {\n        // accepted solution\n    }\n}\n",
}

COMMUNITY = {
    "arrays": [("priya_sharma", "Kadane's trick that finally clicked for me: reset the running sum when it goes negative, because a negative prefix can only hurt."),
               ("arjun_mehta", "For Two Sum, is the hash map approach always better than sorting + two pointers?"),
               ("rahul_verma", "Hash map is O(n) but loses the original order if you sort first — and the problem wants original indices, so hash map wins.")],
    "strings": [("ananya_iyer", "Sliding window template for substring problems: expand right, shrink left while invalid, update answer."),
                ("sneha_patil", "Thanks! That fixed my Longest Substring solution.")],
    "stack-queue": [("rahul_verma", "Monotonic stack = 'keep popping while the new element beats the top'. Next Greater Element is the classic one.")],
    "trees": [("kabir_singh", "How do you parse the level-order input with nulls in the Maximum Depth problem?"),
              ("priya_sharma", "Use a queue of nodes; read two values per node for left and right, skipping nulls.")],
    "dynamic-programming": [("demo", "Coin Change: why does greedy fail for coins [1, 3, 4] and amount 6?"),
                            ("priya_sharma", "Greedy takes 4+1+1 (3 coins) but 3+3 is 2 coins. That's exactly why it needs DP.")],
}

MENTOR_CHAT = [("user", "Hi! I'm stuck on Coin Change. Should I start with recursion?"),
               ("admin", "Yes — write the recursive version first, then add memoization. Think of dp[x] as the fewest coins for amount x."),
               ("user", "That worked, thanks! Now it passes all test cases.")]

NOTES = [("Dynamic Programming", "DP checklist", "1) Define state  2) Transition  3) Base case  4) Order of filling  5) Answer location."),
         ("Graphs", "BFS vs DFS", "BFS → shortest path in unweighted graphs (queue). DFS → connectivity, cycles, topological order (stack/recursion)."),
         ("Binary Search", "lo <= hi or lo < hi?", "Use lo <= hi when searching for an exact value; lo < hi when narrowing to a boundary (first true)."),
         ("Arrays", "Kadane in one line", "cur = max(x, cur + x); best = max(best, cur)")]


# ---------------------------------------------------------------- build
def build_cases():
    out = []
    for title, diff, desc, solver, inputs in PROBLEMS:
        cases = [{"input": i + "\n", "output": solver(i) + "\n"} for i in inputs]
        out.append((title, diff, desc, cases))
    return out


def main():
    from app import create_app
    from app.extensions import db
    from app.models.announcement import Announcement
    from app.models.badge import Badge, UserBadge
    from app.models.chat_message import ChatMessage
    from app.models.coding_question import CodingQuestion
    from app.models.coding_question_progress import CodingQuestionProgress
    from app.models.coding_test import CodingTest
    from app.models.coding_test_progress import CodingTestProgress
    from app.models.community_message import CommunityMessage
    from app.models.flash_note import FlashNote
    from app.models.submission import Submission
    from app.models.topic import Topic, UserTopicProgress
    from app.models.user import User
    from app.models.user_notification import UserNotification

    problems = build_cases()   # fails loudly if a reference solution breaks
    app = create_app()
    db_path = os.path.join(app.instance_path, "site.db")
    if os.path.exists(db_path):
        backup = os.path.join(app.instance_path, f"site_backup_{datetime.now():%Y%m%d_%H%M%S}.db")
        shutil.copy(db_path, backup)
        print(f"Backed up old database to {backup}")

    rng = random.Random(42)
    now = datetime.utcnow()
    with app.app_context():
        db.drop_all()
        db.create_all()

        topics = {}
        for title, tags, desc in TOPICS:
            topics[title] = Topic(title=title, tags=tags, description=desc)
            db.session.add(topics[title])
        questions = {}
        for title, diff, desc, cases in problems:
            first = cases[0]
            q = CodingQuestion(title=title, difficulty=diff.capitalize(), description=desc,
                               sample_input=first["input"].rstrip("\n"), sample_output=first["output"].rstrip("\n"),
                               test_cases=json.dumps(cases))
            questions[title] = q
            db.session.add(q)
        db.session.flush()

        tests = []
        for i, (title, desc, qtitles, ttitles) in enumerate(TESTS):
            t = CodingTest(title=title, description=desc, created_at=now - timedelta(days=20 - i * 7))
            t.questions.extend(questions[x] for x in qtitles)
            t.topics.extend(topics[x] for x in ttitles)
            db.session.add(t)
            tests.append((t, qtitles))

        with redirect_stdout(io.StringIO()):
            from app.routes.badge import init_badges
            init_badges()

        users = {}
        for idx, (uname, email, skill) in enumerate(LEARNERS):
            u = User(username=uname, email=email, password=generate_password_hash("demo1234"), xp=0,
                     created_at=now - timedelta(days=60 - idx * 4))
            db.session.add(u)
            users[uname] = (u, skill)
        db.session.flush()

        xp_map = {"easy": 10, "medium": 20, "hard": 30}
        topic_list = list(topics.values())
        q_list = list(questions.values())
        for uname, (u, skill) in users.items():
            xp = 0
            # topics: earlier topics more likely completed
            for k, t in enumerate(topic_list):
                p_open = max(0.1, skill + 0.35 - k * 0.04)
                if rng.random() > p_open:
                    continue
                completed = rng.random() < skill + 0.15 - k * 0.02
                quiz = completed and rng.random() < 0.7
                opened = now - timedelta(days=rng.randint(0, 28), hours=rng.randint(0, 23))
                db.session.add(UserTopicProgress(
                    user_id=u.id, topic_id=t.id, completed=completed, quiz_passed=quiz,
                    completed_at=opened + timedelta(minutes=rng.randint(10, 90)) if completed else None,
                    revision_count=rng.randint(1, 6), total_time_spent=rng.randint(240, 2700),
                    bookmarked=rng.random() < 0.2, last_accessed_at=opened))
                xp += (10 if completed else 0) + (10 if quiz else 0)
            # practice submissions
            for k, q in enumerate(q_list):
                diff = q.difficulty.lower()
                if rng.random() > skill + 0.25 - (0.15 if diff == "hard" else 0.05 if diff == "medium" else 0):
                    continue
                total = len(json.loads(q.test_cases))
                attempts = rng.randint(1, 3)
                solved = rng.random() < skill + (0.25 if diff == "easy" else 0)
                lang = rng.choice(["python", "python", "cpp", "java"])
                when = now - timedelta(days=rng.randint(0, 29), hours=rng.randint(0, 23))
                for a in range(attempts):
                    last = a == attempts - 1
                    passed = total if (solved and last) else rng.randint(0, total - 1)
                    db.session.add(Submission(user_id=u.id, question_id=q.id, code=CODE_OK[lang], language=lang,
                                              status="Passed" if passed == total else "Failed", passed=passed, total=total,
                                              runtime=round(rng.uniform(2, 40), 1), solve_time=rng.randint(120, 1800),
                                              created_at=when + timedelta(minutes=a * 7)))
                db.session.add(CodingQuestionProgress(user_id=u.id, question_id=q.id, is_completed=solved, xp_awarded=solved,
                                                      solved_at=when if solved else None, last_attempt_at=when))
                if solved:
                    xp += 10
            # coding tests
            for t, qtitles in tests:
                if rng.random() > skill + 0.2:
                    continue
                for qt in qtitles:
                    q = questions[qt]
                    ok = rng.random() < skill + (0.2 if q.difficulty.lower() == "easy" else -0.1)
                    db.session.add(CodingTestProgress(user_id=u.id, test_id=t.id, question_id=q.id,
                                                      status="Passed" if ok else "Failed", time_taken=rng.randint(60, 600),
                                                      xp_awarded=ok, attempted_at=now - timedelta(days=rng.randint(0, 14))))
                    if ok:
                        xp += xp_map[q.difficulty.lower()]
            u.xp = xp
        db.session.flush()
        for u, _ in users.values():
            with redirect_stdout(io.StringIO()):
                u.check_and_award_badges()
            highest = u.get_highest_earned_badge() if hasattr(u, "get_highest_earned_badge") else None
            if highest is not None and rng.random() < 0.5:
                u.equipped_badge_id = highest.id

        for title, content, days_ago in ANNOUNCEMENTS:
            a = Announcement(title=title, content=content, created_at=now - timedelta(days=days_ago))
            db.session.add(a)
            db.session.flush()
            for u, _ in users.values():
                db.session.add(UserNotification(user_id=u.id, announcement_id=a.id,
                                                is_read=days_ago > 5 and rng.random() < 0.8, is_removed=False,
                                                created_at=a.created_at))

        for group, msgs in COMMUNITY.items():
            for k, (uname, text) in enumerate(msgs):
                u = users[uname][0]
                db.session.add(CommunityMessage(group_key=group, user_id=u.id, sender_name=u.username, is_admin=False,
                                                message=text, created_at=now - timedelta(days=len(msgs) - k, hours=rng.randint(0, 5))))
        db.session.add(CommunityMessage(group_key="arrays", user_id=None, sender_name="Admin", is_admin=True,
                                        message="Great discussion! Pin this: always ask whether the input is sorted before choosing an approach.",
                                        created_at=now - timedelta(hours=6)))

        for uname in ("demo", "arjun_mehta", "kabir_singh"):
            u = users[uname][0]
            for k, (sender, text) in enumerate(MENTOR_CHAT):
                db.session.add(ChatMessage(user_id=u.id, sender_type=sender, message=text,
                                           created_at=now - timedelta(days=2, hours=-k)))
        demo = users["demo"][0]
        for k, (subject, title, content) in enumerate(NOTES):
            db.session.add(FlashNote(user_id=demo.id, subject=subject, title=title, content=content,
                                     created_at=now - timedelta(days=10 - k), updated_at=now - timedelta(days=10 - k)))
        db.session.commit()

        print(f"Seeded {Topic.query.count()} topics, {CodingQuestion.query.count()} problems, {CodingTest.query.count()} tests, "
              f"{User.query.count()} learners, {Submission.query.count()} submissions, {Badge.query.count()} badges.")
        print("Learner login: demo@edumentor.dev / demo1234   ·   Admin login: admin / admin123")


if __name__ == "__main__":
    sys.exit(main())
