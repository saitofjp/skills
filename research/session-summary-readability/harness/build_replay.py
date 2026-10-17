#!/usr/bin/env python3
"""Turn a past session into a Claude Code transcript that can be resumed.

The session comes as records.jsonl, the file that
skills/semantic-structure/scripts/session_transcript.py `collect` writes.
Only text is replayed: what the user typed, and what Claude wrote in each turn
with a short marker for each tool call. Tool results and thinking are left out.

  build_replay.py RECORDS.jsonl CWD [--upto N]

Writes ~/.claude/projects/<CWD as a slug>/<new id>.jsonl and prints the new
session id, so that `cd CWD && claude --resume <id> --fork-session -p "..."`
continues the session as if its next message were that prompt. --upto keeps
turns 0..N only. A turn starts at a message the user typed; consecutive user
messages share one turn.
"""

import json
import os
import re
import sys
import uuid


def turns_of(path):
    recs = [json.loads(line) for line in open(path)]
    recs = [r for r in recs if not r.get("system")]
    recs.sort(key=lambda r: r["ts"])
    turns = []
    for r in recs:
        text = "\n".join(p[1] if p[0] == "text" else f"（ツール実行: {p[1]}）" for p in r["parts"])
        if r["role"] == "user":
            if turns and not turns[-1]["a"]:
                turns[-1]["u"].append(text)
            else:
                turns.append({"u": [text], "a": []})
        elif turns:
            turns[-1]["a"].append(text)
    return turns


def main():
    records, cwd = sys.argv[1], os.path.abspath(sys.argv[2])
    turns = turns_of(records)
    if "--upto" in sys.argv:
        turns = turns[: int(sys.argv[sys.argv.index("--upto") + 1]) + 1]
    sid = str(uuid.uuid4())
    folder = os.path.expanduser(f"~/.claude/projects/{re.sub(r'[^A-Za-z0-9]', '-', cwd)}")
    os.makedirs(folder, exist_ok=True)
    common = {"isSidechain": False, "userType": "external", "cwd": cwd, "sessionId": sid,
              "version": "2.1.302", "timestamp": "2026-01-01T00:00:00.000Z"}
    lines, parent = [], None
    for i, t in enumerate(turns):
        u = str(uuid.uuid4())
        lines.append({**common, "parentUuid": parent, "type": "user", "uuid": u,
                      "message": {"role": "user", "content": "\n\n".join(t["u"])}})
        parent = u
        if t["a"]:
            a = str(uuid.uuid4())
            lines.append({**common, "parentUuid": parent, "type": "assistant", "uuid": a,
                          "message": {"id": f"msg_replay_{i}", "type": "message", "role": "assistant",
                                      "model": "claude-opus-5-5", "stop_reason": "end_turn", "stop_sequence": None,
                                      "usage": {"input_tokens": 0, "output_tokens": 0},
                                      "content": [{"type": "text", "text": "\n\n".join(t["a"])}]}})
            parent = a
    with open(f"{folder}/{sid}.jsonl", "w") as f:
        for line in lines:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    print(sid)


if __name__ == "__main__":
    main()
