#!/usr/bin/env python3
"""Keep the files shared by the semantic skills identical.

Each skill must work when installed alone, so semantic-structure-builder,
semantic-structure-viewer and semantic-structure-reconstructor each carry their own
copy of the Semantic Structure contract and its tool. The builder's copy is the original.

  python3 scripts/sync_semantic_shared.py          # copy builder -> the others
  python3 scripts/sync_semantic_shared.py --check  # exit 1 if the copies differ
"""

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "skills" / "semantic-structure-builder"
COPIES = [ROOT / "skills" / "semantic-structure-viewer", ROOT / "skills" / "semantic-structure-reconstructor"]
SHARED = ["references/semantic-structure.md", "scripts/semantic_structure.py"]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="only report differences")
    args = parser.parse_args()
    stale = []
    for target in COPIES:
        for rel in SHARED:
            src, dst = SOURCE / rel, target / rel
            if dst.exists() and filecmp.cmp(src, dst, shallow=False):
                continue
            stale.append(dst.relative_to(ROOT))
            if not args.check:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
    if args.check:
        for path in stale:
            print(f"out of date: {path}")
        return 1 if stale else 0
    for path in stale:
        print(f"updated {path}")
    if not stale:
        print("already in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
