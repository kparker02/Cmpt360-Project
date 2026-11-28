# Kyle Parker, kyp424, 11279181
from itertools import product
from collections import Counter

"""
Helper function used in baseline algorithm
"""
def fits(S, X):
    pos = -1
    for ch in X * 3:
        pos = S.find(ch, pos + 1)
        if pos < 0:
            return False
    return True


"""
Baseline Bruteforce algorithm to solve Longest Cubic Subsequence problem
"""
def baseline(S, stats=None):
    cnt = Counter(S)
    alphabet = sorted(ch for ch, c in cnt.items() if c >= 3)
    m = len(S) // 3
    checked = 0

    result = ""
    if alphabet:
        found = False
        for L in range(m, 0, -1):
            for tup in product(alphabet, repeat=L):
                checked += 1
                X = "".join(tup)
                if fits(S, X):
                    result = X * 3
                    found = True
                    break
            if found:
                break
    if stats is not None:
        stats["checked"] = checked
        stats["sigma_prime"] = len(alphabet)
        stats["m"] = m
    return result


"""
Longest Cubic subsequence: first attempt
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
First Attempt which was flawed but used splits
"""
def first_try(S):
    # This algorithm turns out to be flawed as it only examines one pair of split points
    n = len(S)
    i, j = n // 3, 2 * n // 3
    X = lcs3(S[:i], S[i:j], S[j:])
    return X * 3


"""
Base testing
"""
if __name__ == "__main__":
    tests = ["aaabbbccc", "atcgtatgcatgca", "abcabcab", "abcabcabcxyzxyzxyz", "aaa"]
    for S in tests:
        first = first_try(S)
        second = baseline(S)
        print(f"S = {S}")
        print(f" first try : {first!r} (length {len(first)})")
        print(f" baseline : {second!r} (length {len(second)})")