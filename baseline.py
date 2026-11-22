# Kyle Parker, kyp424, 11279181


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
            x -= 1
    return "".join(reversed(out))

def first_try(S):
    n = len(S)
    i, j = n // 3, 2 * n // 3
    X = lcs3(S[:i], S[i:j], S[j:])
    return X * 3

tests = ["aaabbbccc", "atcgtatgcatgca"]
for S in tests:
    first = first_try(S)
    print(f"S = {S}")
    print(f" fixed thirds : {first!r} (length {len(first)})")