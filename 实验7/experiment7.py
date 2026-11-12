"""实验7：回溯法。仅依赖 Python 标准库。"""
from itertools import permutations, product

INF = float("inf")


def nonnegative_ints(values):
    if any(type(x) is not int or x < 0 for x in values):
        raise ValueError("Expected nonnegative integers")


def knapsack_bt(w, v, capacity):
    if len(w) != len(v):
        raise ValueError("Length mismatch")
    nonnegative_ints(list(w) + list(v) + [capacity])
    n = len(w)
    # 按单位重量价值降序，便于计算上界；重量为 0 的排最前
    order = sorted(range(n), key=lambda i: (
        -(v[i] / w[i]) if w[i] else -INF, i))
    ws = [w[i] for i in order]
    vs = [v[i] for i in order]
    best = {"value": 0, "x": [0] * n, "nodes": 0}
    x = [0] * n

    def bound(i, cw, cv):
        left = capacity - cw
        while i < n and ws[i] <= left:
            left -= ws[i]
            cv += vs[i]
            i += 1
        if i < n:
            cv += vs[i] * left / ws[i]
        return cv

    def backtrack(i, cw, cv):
        best["nodes"] += 1
        if i == n:
            if cv > best["value"]:
                best["value"], best["x"] = cv, x[:]
            return
        if cw + ws[i] <= capacity:          # 约束函数剪左子树
            x[i] = 1
            backtrack(i + 1, cw + ws[i], cv + vs[i])
            x[i] = 0
        if bound(i + 1, cw, cv) > best["value"]:  # 限界剪右子树
            backtrack(i + 1, cw, cv)

    backtrack(0, 0, 0)
    chosen = sorted(order[i] + 1 for i in range(n) if best["x"][i])
    return best["value"], chosen, best["nodes"]


def tsp_bt(c):
    n = len(c)
    if any(len(row) != n for row in c):
        raise ValueError("Expected square matrix")
    for i in range(n):
        for j in range(n):
            if i != j and c[i][j] is not None:
                nonnegative_ints([c[i][j]])
            if c[i][j] != c[j][i]:
                raise ValueError("Weights must be symmetric")
    if n == 0:
        return 0, [], 0
    if n == 1:
        return 0, [1, 1], 0

    def edge(i, j):
        return INF if c[i][j] is None else c[i][j]

    path = list(range(n))
    best = {"cost": INF, "tour": None, "nodes": 0}

    def backtrack(i, cw):
        best["nodes"] += 1
        if i == n:
            total = cw + edge(path[n - 1], path[0])
            if total < best["cost"]:
                best["cost"], best["tour"] = total, path[:]
            return
        for j in range(i, n):
            cost = cw + edge(path[i - 1], path[j])
            if cost < best["cost"]:         # 剪去不优于当前最优的分支
                path[i], path[j] = path[j], path[i]
                backtrack(i + 1, cost)
                path[i], path[j] = path[j], path[i]

    backtrack(1, 0)
    if best["tour"] is None:
        return INF, [], best["nodes"]
    tour = [k + 1 for k in best["tour"]] + [1]
    return best["cost"], tour, best["nodes"]


def m_coloring(n, edges, m):
    nonnegative_ints([n, m])
    adj = [[False] * n for _ in range(n)]
    for a, b in edges:
        if not (1 <= a <= n and 1 <= b <= n) or a == b:
            raise ValueError("Bad edge")
        adj[a - 1][b - 1] = adj[b - 1][a - 1] = True
    color = [0] * n
    result = {"count": 0, "first": None, "nodes": 0}

    def ok(k):
        return all(not (adj[k][j] and color[j] == color[k])
                   for j in range(k))

    def backtrack(k):
        result["nodes"] += 1
        if k == n:
            result["count"] += 1
            if result["first"] is None:
                result["first"] = color[:]
            return
        for col in range(1, m + 1):
            color[k] = col
            if ok(k):
                backtrack(k + 1)
        color[k] = 0

    backtrack(0)
    return result["count"], result["first"], result["nodes"]


def chromatic_number(n, edges):
    for m in range(0 if n == 0 else 1, n + 1):
        if m_coloring(n, edges, m)[0]:
            return m
    return 0


def expect_error(func, *args):
    try:
        func(*args)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")


def main():
    w, v, capacity = [3, 5, 2, 1], [9, 10, 7, 4], 7
    c = [[0, 30, 6, 4],
         [30, 0, 5, 10],
         [6, 5, 0, 20],
         [4, 10, 20, 0]]
    n, m = 5, 3
    edges = [(1, 2), (1, 3), (1, 4), (2, 3),
             (2, 5), (3, 4), (3, 5), (4, 5)]

    value, chosen, nodes = knapsack_bt(w, v, capacity)
    masks = list(product((0, 1), repeat=len(w)))
    oracle = max(sum(vi * x for vi, x in zip(v, mask))
                 for mask in masks
                 if sum(wi * x for wi, x in zip(w, mask)) <= capacity)
    assert value == oracle == 20
    assert sum(w[i - 1] for i in chosen) <= capacity
    assert sum(v[i - 1] for i in chosen) == value
    print("Knapsack:", value, "items =", chosen,
          "weight =", sum(w[i - 1] for i in chosen))
    print("  visited nodes =", nodes, "(full tree = 31)")

    cost, tour, nodes = tsp_bt(c)
    def length(t):
        return sum(c[t[k]][t[k + 1]] for k in range(len(t) - 1))
    tours = [(0,) + p + (0,) for p in permutations(range(1, 4))]
    oracle = min(map(length, tours))
    assert cost == oracle == length([k - 1 for k in tour]) == 25
    assert tour[0] == tour[-1] == 1 and sorted(tour[:-1]) == [1, 2, 3, 4]
    print("TSP:", cost, "tour =", "-".join(map(str, tour)))
    print("  visited nodes =", nodes, "(full tree = 16)")

    count, first, nodes = m_coloring(n, edges, m)
    def valid(col):
        return all(col[a - 1] != col[b - 1] for a, b in edges)
    oracle = sum(valid(p) for p in product(range(1, m + 1), repeat=n))
    assert count == oracle and valid(first)
    k = chromatic_number(n, edges)
    assert m_coloring(n, edges, k - 1)[0] == 0
    print("Coloring: m =", m, "solutions =", count, "first =", first)
    print("  visited nodes =", nodes, "(full tree = 364)")
    print("  chromatic number =", k)
    print("Exhaustive cases: bag=16, TSP=6, coloring=243")

    assert knapsack_bt([], [], 10)[:2] == (0, [])
    assert knapsack_bt([2], [3], 0)[:2] == (0, [])
    assert knapsack_bt([0, 2], [5, 3], 0)[:2] == (5, [1])
    assert knapsack_bt([1, 1], [2, 2], 5)[:2] == (4, [1, 2])
    assert tsp_bt([[0]])[:2] == (0, [1, 1])
    assert tsp_bt([[0, 3], [3, 0]])[:2] == (6, [1, 2, 1])
    assert tsp_bt([[0, None, 1], [None, 0, 1],
                   [1, 1, 0]])[0] == INF
    assert m_coloring(0, [], 1)[0] == 1
    assert m_coloring(3, [(1, 2), (2, 3), (1, 3)], 2)[0] == 0
    assert m_coloring(3, [(1, 2), (2, 3), (1, 3)], 3)[0] == 6
    assert m_coloring(2, [], 2)[0] == 4
    assert chromatic_number(4, [(1, 2), (2, 3), (3, 4), (4, 1)]) == 2

    expect_error(knapsack_bt, [2], [], 10)
    expect_error(knapsack_bt, [2], [3], -1)
    expect_error(tsp_bt, [[0, 1], [2, 0]])
    expect_error(tsp_bt, [[0, -1], [-1, 0]])
    expect_error(m_coloring, 2, [(1, 3)], 2)
    expect_error(m_coloring, 2, [(1, 2)], -1)
    print("Boundary checks: 12; invalid inputs: 6")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
