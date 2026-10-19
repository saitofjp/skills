#!/bin/bash
# Evaluate one summary from run_condition.sh.
#
#   eval_summary.sh RUNDIR NAME UPTO
#
# Needs $WORK/gt_NAME.md (the answer key: purpose, current conclusion, the
# branches that were set aside). Writes RUNDIR/eval/:
#   doc.md      the summary (the largest file the model wrote, or its reply)
#   reader_*.txt a model that never saw the session reads doc.md only
#   judge.txt   structure and the reader's answers, checked against the key
#   self.txt    the model that wrote it rates it for a reader who missed the session
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=${WORK:-$PWD/work}
R=$1; N=$2; U=$3
mkdir -p "$R/eval" "$WORK/tmpcwd"; cd "$WORK/tmpcwd"
python3 - "$R" <<'PY'
import glob, os, re, sys
R = sys.argv[1]
doc = None
files = [f for f in glob.glob(f"{R}/files/*") if f.endswith((".md", ".html", ".txt"))]
if files:
    f = max(files, key=os.path.getsize)
    t = open(f, errors="replace").read()
    if f.endswith(".html"):
        t = re.sub(r"(?is)<(script|style).*?</\1>", "", t)
        t = re.sub(r"\n\s*\n+", "\n\n", re.sub(r"<[^>]+>", "\n", t))
    if len(t) > 1500:
        doc = t
open(f"{R}/eval/doc.md", "w").write(doc if doc is not None else open(f"{R}/answer.md").read())
PY
NOTOOLS=(--tools "" --strict-mcp-config)
for M in ${READERS:-claude-opus-5-5}; do
  { cat "$HERE/reader_prompt.txt"; cat "$R/eval/doc.md"; printf '\n</資料>\n'; } \
    | claude -p --model "$M" "${NOTOOLS[@]}" > "$R/eval/reader_$M.txt" 2>/dev/null
done
{ cat "$HERE/judge_prompt.txt"
  printf '\n<A 正解>\n'; cat "$WORK/gt_$N.md"; printf '</A>\n<B 元セッション>\n'
  python3 "$HERE/transcript_text.py" "$WORK/sessions/$N/records.jsonl" "$U" --num
  printf '</B>\n<C まとめ資料>\n'; cat "$R/eval/doc.md"
  printf '\n</C>\n<D 初見読者の回答>\n'; cat "$R/eval/reader_claude-opus-5-5.txt"; printf '\n</D>\n'
} | claude -p --model claude-opus-5-5 "${NOTOOLS[@]}" > "$R/eval/judge.txt" 2>/dev/null
SID=$(cat "$R/session_id" 2>/dev/null)
if [ -n "$SID" ]; then
  cd "$R/cwd" && claude --resume "$SID" --fork-session --model claude-opus-5-5 "${NOTOOLS[@]}" \
    -p '今のまとめ（資料）を、このセッションを見ていない同僚がいきなり読むとします。その人にとっての読みやすさを1〜5で採点し（5=すぐ要点が掴める）、迷いそうな箇所を最大3つ挙げて。出力は {"score": 数値, "issues": ["..."]} のJSONだけ。' \
    < /dev/null > "$R/eval/self.txt" 2>/dev/null
fi
echo "eval done $R"
