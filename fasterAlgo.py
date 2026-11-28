# Kyle Parker, kyp424, 11279181

from collections import Counter


"""
Same lcs3 as original attempt, now used in fastest algorithm
"""
def lcs3(a, b, c):
    "Returns the subsequence itself"
    la, lb, lc = len(a), len(b), len(c)
    dp = [[[0] * (lc + 1) for _ in range(lb + 1)] for _ in range(la + 1)]

    for x in range(1, la + 1):
        for y in range(1, lb +1):
            for z in range(1, lc + 1):
                if a[x-1] == b[y-1] == c[z-1]:
                    dp[x][y][z] = dp[x-1][y-1][z-1] + 1
                else:
                    dp[x][y][z] = max(dp[x-1][y][z],
                                      dp[x][y-1][z],
                                      dp[x][y][z-1])

    out = []
    x, y, z = la, lb, lc
    while x > 0 and y > 0 and z > 0:
        cur = dp[x][y][z]
        if (a[x-1] == b[y-1] == c[z-1] and cur == dp[x-1][y-1][z-1] + 1):
            out.append(a[x-1])
            x, y, z = x - 1, y - 1, z - 1
        elif dp[x-1][y][z] == cur:
            x -= 1
        elif dp[x][y-1][z] == cur:
            y -= 1
        else:
            z -= 1
    return "".join(reversed(out))


"""
Length of the 3-way LCS using two rolling layers over a
"""
def lcs3_length(a, b, c):
    lb, lc = len(b), len(c)
    prev = [[0] * (lc + 1) for _ in range(lb + 1)]
    for ch in a:
        cur = [[0] * (lc + 1) for _ in range(lb + 1)]
        for y in range(1, lb + 1):
            by = b[y - 1]
            p_y, p_ym = prev[y], prev[y - 1]
            c_y, c_ym = cur[y], cur[y - 1]
            for z in range(1, lc + 1):
                if ch == by == c[z - 1]:
                    c_y[z] = p_ym[z - 1] + 1
                else:
                    v = p_y[z]
                    w = c_ym[z]
                    if w > v:
                        v = w
                    w = c_y[z - 1]
                    if w > v:
                        v = w
                    c_y[z] = v
        prev = cur
    return prev[lb][lc]


"""
Attempt faster algorithm using dynamic programming and algorithm outlined in paper titled
"The Longest Subsequence-Repeated Subsequence Problem",
written by Manuel Lafond, Wenfeng Lai, Adiesha Liyanage and Binhai Zhu
"""
def faster(S):
    n = len(S)
    best = ""
    for i in range(n + 1):
        for j in range(i, n + 1):
            X = lcs3(S[:i], S[i:j], S[j:])
            if len(X) > len(best):
                best = X
    return best * 3



"""
Improvement upon Dynamic programmed solution using pruning
"""
def fastest(S):
    cnt = Counter(S)
    T = "".join(ch for ch in S if cnt[ch] >= 3)
    n = len(T)
    if n < 3:
        return ""
    syms = sorted(set(T))

    pre = {s: [0] * (n + 1) for s in syms}
    for k, ch in enumerate(T):
        for s in syms:
            pre[s][k + 1] = pre[s][k] + (1 if s == ch else 0)

    cand = []
    for i in range(1, n):
        for j in range(i + 1, n):
            u = 0
            for s in syms:
                p = pre[s]
                u += min(p[i], p[j] - p[i], p[n] - p[j])
            if u > 0:
                cand.append((-u, i, j))
    cand.sort()

    best, best_split = 0, None
    for neg_u, i, j, in cand:
        if -neg_u <= best:
            break
        allowed = { s for s in syms
                   if min(pre[s][i], pre[s][j] - pre[s][i],
                          pre[s][n] - pre[s][j]) > 0}
        A = [ch for ch in T[:i] if ch in allowed]
        B = [ch for ch in T[i:j] if ch in allowed]
        C = [ch for ch in T[j:] if ch in allowed]
        L = lcs3_length(A, B, C)
        if L > best:
            best, best_split = L, (A, B, C)

    if best_split is None:
        return ""
    return lcs3(*best_split) * 3



"""
Base testing
"""
if __name__ == "__main__":
    tests = ["aaabbbccc", "atcgtatgcatgca", "abcabcab", "abcabcabcxyzxyzxyz", "aaa"]
    for S in tests:
        fast1 = faster(S)
        fast2 = fastest(S)
        print(f"S = {S}")
        print(f" fixed thirds : {fast1!r} (length {len(fast1)})")
        print(f" fixed thirds, pruning : {fast2!r} (length {len(fast2)})")
