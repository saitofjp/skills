#!/usr/bin/env python3
"""Check whether the installed review-birds-eye skill is invoked for each query.

  python3 evals/check_trigger.py evals/trigger-eval.json [--workers 8]

Runs `claude -p QUERY` from the repository root, one turn per query, and records
the first tool call. A query counts as triggering when that call is the Skill
tool with review-birds-eye.

skill-creator's run_eval.py does not work in this repository: it installs a
temporary copy of the skill under another name and counts calls to that name,
but the real skill is already installed in .claude/skills, so Claude calls the
real one and every query counts as not triggering. This script counts calls to
the real skill instead. Standard library only.
"""

import argparse
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = "review-birds-eye"


def first_tool(query):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    p = subprocess.Popen(
        ["claude", "-p", query, "--output-format", "stream-json", "--verbose", "--max-turns", "1"],
        cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    try:
        for line in p.stdout:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") != "assistant":
                continue
            for block in event["message"].get("content", []):
                if block.get("type") == "tool_use":
                    name = block["name"]
                    return name + (":" + block["input"].get("skill", "") if name == "Skill" else "")
    finally:
        p.kill()
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("eval_set")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    queries = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    with ThreadPoolExecutor(args.workers) as pool:
        firsts = list(pool.map(lambda q: first_tool(q["query"]), queries))
    passed = 0
    for q, first in zip(queries, firsts):
        ok = (first == "Skill:" + SKILL) == q["should_trigger"]
        passed += ok
        print("OK" if ok else "NG", "should   " if q["should_trigger"] else "shouldn't", "|", first, "|", q["query"])
    print(f"{passed} / {len(queries)}")
    return 0 if passed == len(queries) else 1


if __name__ == "__main__":
    raise SystemExit(main())
