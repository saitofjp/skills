#!/usr/bin/env python3
"""Print a past session as plain text, for handing it to a model as a document.

  transcript_text.py RECORDS.jsonl UPTO [--num] [--shuffle]

RECORDS.jsonl is what session_transcript.py `collect` writes. Turns 0..UPTO are
printed as 【ユーザー】 / 【AI】 blocks. --num labels each block with its turn
number (Tn). --shuffle prints the turns in a fixed random order, to see whether
a summary follows the order it was given or rebuilds its own.
"""

import random
import sys

from build_replay import turns_of


def main():
    turns = turns_of(sys.argv[1])
    picked = list(enumerate(turns[: int(sys.argv[2]) + 1]))
    if "--shuffle" in sys.argv:
        random.Random(7).shuffle(picked)
    for i, t in picked:
        tag = f"T{i} " if "--num" in sys.argv else ""
        print(f"【{tag}ユーザー】\n" + "\n\n".join(t["u"]) + "\n")
        if t["a"]:
            print(f"【{tag}AI】\n" + "\n\n".join(t["a"]) + "\n")


if __name__ == "__main__":
    main()
