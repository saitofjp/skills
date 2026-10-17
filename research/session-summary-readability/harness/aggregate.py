#!/usr/bin/env python3
"""Collect the evaluations of every run into one table.

  aggregate.py [WORK] [-o results.tsv]

Prints one row per run and, after it, the mean of each column per condition
(all sessions pooled). rho is the rank correlation between the order of the
summary's sections and the turn each section first came from: near 1 means the
summary walks through the session in the order it happened.
"""

import glob
import json
import os
import re
import statistics
import sys


def load_json(path):
    try:
        return json.loads(re.search(r"\{.*\}", open(path).read(), re.S).group(0))
    except Exception:
        return {}


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r, i = [0.0] * len(v), 0
    while i < len(v):
        k = i
        while k + 1 < len(v) and v[order[k + 1]] == v[order[i]]:
            k += 1
        for m in range(i, k + 1):
            r[order[m]] = (i + k) / 2
        i = k + 1
    return r


def spearman(turns):
    t = [x for x in turns if isinstance(x, int)]
    if len(t) < 3:
        return None
    a, b = ranks(list(range(len(t)))), ranks(t)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va, vb = sum((x - ma) ** 2 for x in a), sum((y - mb) ** 2 for y in b)
    if not va or not vb:
        return None
    return round(sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) ** 0.5, 2)


COLS = ["run", "chars", "axis", "rho", "purpose_first", "conclusion_at", "process_refs",
        "set_aside_share", "q1_purpose", "q2_conclusion", "q3_set_aside", "q4_next", "reader_score", "self_score"]


def row(d):
    name = os.path.basename(d)
    j = load_json(f"{d}/eval/judge.txt")
    reader = load_json(f"{d}/eval/reader_claude-opus-5-5.txt")
    own = load_json(f"{d}/eval/self.txt")
    scores = j.get("reader_scores", {})
    doc = open(f"{d}/eval/doc.md").read() if os.path.exists(f"{d}/eval/doc.md") else ""
    return {"run": name, "chars": len(doc), "axis": j.get("axis"),
            "rho": spearman([s.get("t") for s in j.get("sections", [])]),
            "purpose_first": j.get("purpose_upfront"), "conclusion_at": j.get("conclusion_pos_pct"),
            "process_refs": j.get("process_ref_count"), "set_aside_share": j.get("superseded_space_pct"),
            "q1_purpose": scores.get("q1"), "q2_conclusion": scores.get("q2"),
            "q3_set_aside": scores.get("q3"), "q4_next": scores.get("q4"),
            "reader_score": reader.get("q5"), "self_score": own.get("score")}


def main():
    args = [a for a in sys.argv[1:] if a != "-o"]
    out = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else None
    if out in args:
        args.remove(out)
    work = args[0] if args else os.path.join(os.getcwd(), "work")
    rows = [row(d) for d in sorted(glob.glob(f"{work}/runs/*_*_s*")) if os.path.isdir(f"{d}/eval")]
    lines = ["\t".join(COLS)] + ["\t".join("" if r[c] is None else str(r[c]) for c in COLS) for r in rows]
    print("\n".join(lines))
    if out:
        open(out, "w").write("\n".join(lines) + "\n")
    print()
    for cond in sorted({r["run"].split("_")[1] for r in rows}):
        rr = [r for r in rows if r["run"].split("_")[1] == cond]
        cells = [f"{cond} n={len(rr)}", f"purpose_first={sum(1 for r in rr if r['purpose_first'] is True)}/{len(rr)}"]
        for c in COLS[3:]:
            if c == "purpose_first":
                continue
            v = [r[c] for r in rr if isinstance(r[c], (int, float)) and not isinstance(r[c], bool)]
            if v:
                cells.append(f"{c}={statistics.mean(v):.1f}")
        print("  ".join(cells))


if __name__ == "__main__":
    main()
