import time
import random
import string
import csv
import sys
from collections import Counter

from baseline import baseline
from fasterAlgo import faster, fastest, lcs3, lcs3_length


# ----------------------------------------------------------------------------
# Correctness cross-check on small inputs
# ----------------------------------------------------------------------------
def correctness_check():
    """
    On small random inputs, verify all three algorithms agree on the *length*
    of the optimal cubic subsequence.  Baseline is the ground truth.
    Returns (num_tested, num_mismatches, mismatch_examples).
    """
    rng = random.Random(12345)
    mismatches = []
    n_tested = 0

    for trial in range(200):
        n = rng.randint(1, 12)
        sigma = rng.randint(1, 3)
        alphabet = string.ascii_lowercase[:sigma]
        S = "".join(rng.choice(alphabet) for _ in range(n))

        b = baseline(S)
        f1 = faster(S)
        f2 = fastest(S)
        n_tested += 1

        if not (len(b) == len(f1) == len(f2)):
            mismatches.append((S, b, f1, f2))
        # Also verify each returned string is actually a cubic subsequence
        for name, out in [("baseline", b), ("faster", f1), ("fastest", f2)]:
            if out and not _is_valid_cubic_subseq(S, out):
                mismatches.append((S, name, out, "INVALID"))

    return n_tested, mismatches


def _is_valid_cubic_subseq(S, C):
    """Check C == X*X*X is a subsequence of S."""
    if len(C) % 3 != 0:
        return False
    L = len(C) // 3
    X = C[:L]
    if C != X * 3:
        return False
    pos = -1
    for ch in X * 3:
        pos = S.find(ch, pos + 1)
        if pos < 0:
            return False
    return True


# ----------------------------------------------------------------------------
# Timing helpers
# ----------------------------------------------------------------------------
def time_call(fn, S, repeats=1, timeout=None):
    """
    Returns (result_len, best_time_seconds).  If timeout is exceeded,
    returns (None, timeout).
    """
    best = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        out = fn(S)
        dt = time.perf_counter() - t0
        if best is None or dt < best:
            best = dt
        if timeout is not None and dt > timeout:
            return len(out) if out else 0, timeout
    return (len(out) if out else 0), best


# ----------------------------------------------------------------------------
# Generator family 1: random uniform, fixed n, varying alphabet size
# ----------------------------------------------------------------------------
def gen_uniform(rng, n, sigma):
    alphabet = string.ascii_lowercase[:sigma]
    return "".join(rng.choice(alphabet) for _ in range(n))


# ----------------------------------------------------------------------------
# Generator family 2: structured "planted" cubic subsequences
# ----------------------------------------------------------------------------
def gen_planted(rng, n, sigma, block_len=None):
    """
    Build S by planting a cubic subsequence X^3 and then interleaving
    random noise.  Makes lcs3 *not* trivially zero, exercises pruning.
    """
    alphabet = string.ascii_lowercase[:sigma]
    if block_len is None:
        block_len = max(1, n // 9)
    X = "".join(rng.choice(alphabet) for _ in range(block_len))
    core = list(X * 3)
    while len(core) < n:
        core.insert(rng.randint(0, len(core)), rng.choice(alphabet))
    return "".join(core)


# ----------------------------------------------------------------------------
# Generator family 3: high-repetition (all chars appear >= 3 times)
# ----------------------------------------------------------------------------
def gen_repetitive(rng, n, sigma):
    alphabet = string.ascii_lowercase[:sigma]
    base = [rng.choice(alphabet) for _ in range(sigma)]
    S = base * (n // sigma + 1)
    rng.shuffle(S)
    return "".join(S[:n])


# ----------------------------------------------------------------------------
# Experiment 1: scalability in n (fixed sigma=4)
# ----------------------------------------------------------------------------
def exp_scaling_n(out_csv="exp_scaling_n.csv", out_png="exp_scaling_n.png"):
    rng = random.Random(42)
    sigma = 4
    # --- adjust these bounds to keep total runtime reasonable for your machine
    ns_fast = [10, 20, 40, 60, 80, 100, 120, 150, 180]
    ns_base = [4, 6, 8, 10, 12]     # baseline explodes quickly
    ns_fast2 = ns_fast

    rows = []
    # Baseline
    for n in ns_base:
        S = gen_uniform(rng, n, sigma)
        L, t = time_call(baseline, S, repeats=1, timeout=120.0)
        rows.append(dict(algo="baseline", n=n, sigma=sigma,
                         L=L if L is not None else -1, time=t))
        print(f"[baseline] n={n:4d}  L={L}  t={t:.4f}s")
    # faster
    for n in ns_fast:
        S = gen_uniform(rng, n, sigma)
        L, t = time_call(faster, S, repeats=1, timeout=120.0)
        rows.append(dict(algo="faster", n=n, sigma=sigma,
                         L=L if L is not None else -1, time=t))
        print(f"[faster]   n={n:4d}  L={L}  t={t:.4f}s")
    # fastest
    for n in ns_fast2:
        S = gen_uniform(rng, n, sigma)
        L, t = time_call(fastest, S, repeats=1, timeout=120.0)
        rows.append(dict(algo="fastest", n=n, sigma=sigma,
                         L=L if L is not None else -1, time=t))
        print(f"[fastest]  n={n:4d}  L={L}  t={t:.4f}s")

    _write_csv(out_csv, rows)
    _plot_lines(rows, x="n", y="time", series="algo",
                xlabel="n (sequence length)", ylabel="time (s)",
                title=f"Runtime vs n, sigma={sigma} (log-y)",
                out=out_png, logy=True)
    return rows


# ----------------------------------------------------------------------------
# Experiment 2: effect of alphabet size (fixed n)
# ----------------------------------------------------------------------------
def exp_alphabet(out_csv="exp_alphabet.csv", out_png="exp_alphabet.png"):
    rng = random.Random(7)
    n = 90
    sigmas = [2, 3, 4, 5, 6, 8, 10, 14, 20, 26]
    rows = []
    for sigma in sigmas:
        S = gen_uniform(rng, n, sigma)
        Lf, tf = time_call(faster, S, timeout=120.0)
        Ls, ts = time_call(fastest, S, timeout=120.0)
        rows.append(dict(algo="faster", n=n, sigma=sigma, L=Lf, time=tf))
        rows.append(dict(algo="fastest", n=n, sigma=sigma, L=Ls, time=ts))
        print(f"sigma={sigma:3d}  faster L={Lf} t={tf:.4f}s | "
              f"fastest L={Ls} t={ts:.4f}s")

    _write_csv(out_csv, rows)
    _plot_lines(rows, x="sigma", y="time", series="algo",
                xlabel="alphabet size |Sigma|", ylabel="time (s)",
                title=f"Runtime vs alphabet size, n={n}",
                out=out_png, logy=True)
    return rows


# ----------------------------------------------------------------------------
# Experiment 3: structured vs random inputs (fixed n, sigma)
# ----------------------------------------------------------------------------
def exp_input_family(out_csv="exp_input_family.csv",
                     out_png="exp_input_family.png"):
    rng = random.Random(99)
    n, sigma = 120, 4
    gens = {
        "uniform":   lambda: gen_uniform(rng, n, sigma),
        "planted":   lambda: gen_planted(rng, n, sigma),
        "repetitive":lambda: gen_repetitive(rng, n, sigma),
    }
    rows = []
    for name, g in gens.items():
        S = g()
        Lf, tf = time_call(faster, S, timeout=120.0)
        Ls, ts = time_call(fastest, S, timeout=120.0)
        rows.append(dict(algo="faster", family=name, n=n, sigma=sigma,
                         L=Lf, time=tf))
        rows.append(dict(algo="fastest", family=name, n=n, sigma=sigma,
                         L=Ls, time=ts))
        print(f"{name:12s} faster L={Lf} t={tf:.4f}s | "
              f"fastest L={Ls} t={ts:.4f}s")

    _write_csv(out_csv, rows)
    _plot_bars(rows, x="family", y="time", series="algo",
               xlabel="input family", ylabel="time (s)",
               title=f"Runtime by input family (n={n}, sigma={sigma})",
               out=out_png, logy=True)
    return rows


# ----------------------------------------------------------------------------
# Experiment 4: pruning effectiveness -- how many splits fastest examines
# ----------------------------------------------------------------------------
def exp_pruning_effect(out_csv="exp_pruning.csv", out_png="exp_pruning.png"):
    """
    Counts how many split pairs fastest() actually evaluates vs total pairs,
    to measure pruning rate.
    """
    rng = random.Random(5)
    sigma = 4
    ns = [30, 60, 90, 120, 150, 180, 210]
    rows = []
    for n in ns:
        S = gen_uniform(rng, n, sigma)
        cnt = Counter(S)
        T = "".join(ch for ch in S if cnt[ch] >= 3)
        m = len(T)
        total_pairs = max(0, m * (m - 1) // 2)
        # instrument fastest inline
        evaluated, best = _fastest_instrumented(T)
        rows.append(dict(n=n, T_len=m, total_pairs=total_pairs,
                         evaluated=evaluated, best_len=best,
                         prune_ratio=(evaluated / total_pairs
                                      if total_pairs else 0.0)))
        print(f"n={n:4d}  |T|={m:4d}  pairs={total_pairs:6d}  "
              f"evaluated={evaluated:6d}  ratio={rows[-1]['prune_ratio']:.3f}")

    _write_csv(out_csv, rows)
    _plot_lines_xy(rows, x="n", y="prune_ratio",
                   xlabel="n", ylabel="fraction of (i,j) pairs evaluated",
                   title="Pruning effectiveness of fastest()",
                   out=out_png, logy=False)
    return rows


def _fastest_instrumented(T):
    """Same logic as fastest() but returns (evaluated, best_length)."""
    syms = sorted(set(T))
    n = len(T)
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

    best, evaluated = 0, 0
    for neg_u, i, j in cand:
        if -neg_u <= best:
            break
        allowed = {s for s in syms
                   if min(pre[s][i], pre[s][j] - pre[s][i],
                          pre[s][n] - pre[s][j]) > 0}
        A = [ch for ch in T[:i] if ch in allowed]
        B = [ch for ch in T[i:j] if ch in allowed]
        C = [ch for ch in T[j:] if ch in allowed]
        evaluated += 1
        L = lcs3_length(A, B, C)
        if L > best:
            best = L
    return evaluated, best


# ----------------------------------------------------------------------------
# CSV / plotting helpers (kept dependency-light: matplotlib optional)
# ----------------------------------------------------------------------------
def _write_csv(path, rows):
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"  -> wrote {path}")


def _group(rows, series, xkey, ykey):
    groups = {}
    for r in rows:
        groups.setdefault(r[series], []).append((r[xkey], r[ykey]))
    for g in groups.values():
        g.sort()
    return groups


def _plot_lines(rows, x, y, series, xlabel, ylabel, title, out, logy=False):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("  (matplotlib not installed; skipping plot)")
        return
    groups = _group(rows, series, x, y)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name, pts in groups.items():
        xs = [p[0] for p in pts]
        ys = [max(p[1], 1e-6) if logy else p[1] for p in pts]
        ax.plot(xs, ys, marker="o", label=name)
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.set_title(title); ax.legend(); ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)
    print(f"  -> wrote {out}")


def _plot_lines_xy(rows, x, y, xlabel, ylabel, title, out, logy=False):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("  (matplotlib not installed; skipping plot)")
        return
    xs = [r[x] for r in rows]
    ys = [r[y] for r in rows]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(xs, ys, marker="s", color="C3")
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.set_title(title); ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)
    print(f"  -> wrote {out}")


def _plot_bars(rows, x, y, series, xlabel, ylabel, title, out, logy=False):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  (matplotlib/numpy not installed; skipping plot)")
        return
    groups = _group(rows, series, x, y)
    cats = sorted({r[x] for r in rows})
    names = list(groups.keys())
    width = 0.8 / max(1, len(names))
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for k, name in enumerate(names):
        d = dict(groups[name])
        vals = [max(d.get(cat, 1e-6), 1e-6) if logy else d.get(cat, 0.0)
                for cat in cats]
        xs = np.arange(len(cats)) + (k - (len(names)-1)/2) * width
        ax.bar(xs, vals, width=width, label=name)
    ax.set_xticks(range(len(cats))); ax.set_xticklabels(cats)
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.set_title(title); ax.legend(); ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)
    print(f"  -> wrote {out}")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"

    if which in ("all", "correctness"):
        print("=" * 60)
        print("Correctness cross-check (baseline vs faster vs fastest)")
        print("=" * 60)
        n_tested, mismatches = correctness_check()
        print(f"tested {n_tested} random inputs; {len(mismatches)} mismatches")
        for m in mismatches[:10]:
            print("  MISMATCH:", m)

    if which in ("all", "scaling"):
        print("\n" + "=" * 60)
        print("Experiment 1: runtime vs n")
        print("=" * 60)
        exp_scaling_n()

    if which in ("all", "alphabet"):
        print("\n" + "=" * 60)
        print("Experiment 2: runtime vs alphabet size")
        print("=" * 60)
        exp_alphabet()

    if which in ("all", "family"):
        print("\n" + "=" * 60)
        print("Experiment 3: runtime by input family")
        print("=" * 60)
        exp_input_family()

    if which in ("all", "pruning"):
        print("\n" + "=" * 60)
        print("Experiment 4: pruning effectiveness")
        print("=" * 60)
        exp_pruning_effect()